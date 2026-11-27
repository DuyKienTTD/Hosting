#!/usr/bin/env python3
"""KNG-only task *candidate* discovery. Never authorizes dispatch or ACK.

A catalog entry is only discoverable when explicitly marked dispatch_eligible:
true and passes all structural checks. Every other task remains invisible.
Malformed catalog, duplicate IDs/paths, unsafe/missing target -> STOP (exit 2),
not a partial best-effort list. Uses PyYAML SafeLoader, fails closed if absent.
"""
import argparse
import json
import sys
from pathlib import Path, PurePosixPath


class CatalogRejected(ValueError):
    pass


def _load_yaml(path):
    try:
        import yaml
    except ImportError as exc:
        raise CatalogRejected('YAML_DEPENDENCY_MISSING: PyYAML required') from exc

    class UniqueLoader(yaml.SafeLoader):
        pass

    def unique_map(loader, node):
        out = {}
        for key_node, val_node in node.value:
            key = loader.construct_object(key_node, deep=True)
            if not isinstance(key, (str, int, float, bool, type(None))):
                raise CatalogRejected('CATALOG_SCHEMA_INVALID: mapping key type')
            if key in out:
                raise CatalogRejected('CATALOG_DUPLICATE_KEY: ' + str(key))
            out[key] = loader.construct_object(val_node, deep=True)
        return out

    UniqueLoader.add_constructor('tag:yaml.org,2002:map', unique_map)
    try:
        content = path.read_text(encoding='utf-8')
        catalog = yaml.load(content, Loader=UniqueLoader)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        raise CatalogRejected('CATALOG_INVALID: ' + str(exc)) from exc
    return catalog


def select_candidates(root):
    """Returns read-only candidate IDs/paths; never a dispatch authorization."""
    root = Path(root).resolve()
    catalog = _load_yaml(root / 'CATALOG.yaml')
    if not isinstance(catalog, dict) or type(catalog.get('schema_version')) is not int or catalog['schema_version'] != 1:
        raise CatalogRejected('CATALOG_SCHEMA_INVALID: schema_version must be 1')
    docs = catalog.get('documents')
    if not isinstance(docs, list):
        raise CatalogRejected('CATALOG_SCHEMA_INVALID: documents must be a list')
    seen_ids = set()
    seen_paths = set()
    selected = []
    for index, row in enumerate(docs):
        if not isinstance(row, dict):
            raise CatalogRejected(f'CATALOG_SCHEMA_INVALID: documents[{index}]')
        doc_id, rel, kind, status = [row.get(k) for k in ('id','path','type','status')]
        if not isinstance(doc_id, str) or not doc_id.strip() or doc_id != doc_id.strip():
            raise CatalogRejected(f'CATALOG_SCHEMA_INVALID: document id at {index}')
        if doc_id in seen_ids:
            raise CatalogRejected('CATALOG_DUPLICATE_ID: ' + doc_id)
        seen_ids.add(doc_id)
        if not isinstance(rel, str) or not rel or rel.strip() != rel or '\\' in rel:
            raise CatalogRejected('CATALOG_PATH_INVALID: ' + doc_id)
        if rel in seen_paths:
            raise CatalogRejected('CATALOG_DUPLICATE_PATH: ' + rel)
        seen_paths.add(rel)
        p = PurePosixPath(rel)
        if p.is_absolute() or '..' in p.parts or p.as_posix() != rel or rel.startswith('./'):
            raise CatalogRejected('CATALOG_PATH_INVALID: ' + doc_id)
        target = (root / rel).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            raise CatalogRejected('CATALOG_SOURCE_MISSING_OR_UNSAFE: ' + doc_id)
        if not isinstance(kind, str) or not kind or not isinstance(status, str) or not status:
            raise CatalogRejected('CATALOG_SCHEMA_INVALID: type/status for ' + doc_id)
        elig = row.get('dispatch_eligible')
        if elig is not None and type(elig) is not bool:
            raise CatalogRejected('CATALOG_ELIGIBILITY_INVALID: ' + doc_id)
        # Explicit, affirmative, nonarchived task only. Unknown is never true.
        archived = 'archiv' in status.lower() or 'inactive' in status.lower() or 'non-dispatch' in status.lower()
        if kind == 'task' and elig is True and not archived:
            # Only defined states permit manual candidate consideration.
            if status not in ('ready-for-dispatch-review', 'candidate-for-dispatch-review'):
                raise CatalogRejected('TASK_STATUS_UNSUPPORTED: ' + doc_id)
            selected.append({'id': doc_id, 'path': rel})
        elif kind == 'task' and elig is True and archived:
            raise CatalogRejected('ARCHIVED_DISPATCH_CONFLICT: ' + doc_id)
    return selected


def main(argv=None):
    parser = argparse.ArgumentParser(description='List nonauthoritative task candidates; never dispatch or ACK')
    parser.add_argument('--root', default='.', help='repository root')
    args = parser.parse_args(argv)
    try:
        rows = select_candidates(args.root)
    except CatalogRejected as exc:
        print(json.dumps({'status':'STOP', 'error':str(exc), 'candidates':[]}, ensure_ascii=False))
        return 2
    print(json.dumps({'status':'CANDIDATES_ONLY_NOT_AUTHORIZATION', 'candidates':rows}, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    sys.exit(main())
