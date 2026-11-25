---
id: hosting-readset-opt-01-measurements
type: knowledge
status: draft
owner: Chat Dieu phoi
task_id: HOSTING-READSET-OPT-01-IMPL
lifecycle: DURABLE
updated_at: 2026-11-26
sensitivity: public
---
# READ_SET · Số đo 56 ca từ blob Git

[Kế hoạch](README.md) · [Đối chiếu điều khoản](CLAUSE-MAP.md) · [PR #63](https://github.com/DuyKienTTD/Hosting/pull/63).

## Ca đạt giảm ít nhất 30%

| So với | Đơn vị | C0 | C1 | C2 | C3 | C4 | C5 | C6 | Tổng |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `097c080` | Unicode | 0 | 7 | 0 | 0 | 0 | 0 | 0 | **7/56** |
| `097c080` | UTF-8 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | **7/56** |
| `c0720d7` | Unicode | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0/56** |
| `c0720d7` | UTF-8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0/56** |

## Phương pháp và READ_SET

Đọc blob UTF-8 thô qua `git cat-file blob`, kiểm SHA từng blob. PR #63 dùng blob đã stage của chính delta triển khai (SHA từng nguồn ở bảng cuối). Đếm code point Unicode và byte UTF-8, tính cả newline, khoảng trắng, Markdown và metadata. Mỗi path/range tính một lần trong mỗi ca. Đạt ngưỡng khi `10 × PR #63 ≤ 7 × ref so sánh` trên số nguyên. Phần trăm hiển thị hai chữ số, giữ dấu âm cho lượng đọc tăng. Hai snapshot tái lập đúng số liệu POST-04 cho mọi ô và cả hai đơn vị.

Nguồn pin [trước MKOE](https://github.com/DuyKienTTD/Hosting/blob/097c080cc6d7fb3ca36b1849d9c10375d5cbd67f/rules/AGENT_WORKFLOW.md), [MKOE](https://github.com/DuyKienTTD/Hosting/blob/c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb/rules/AGENT_WORKFLOW.md), [đặc tả chung](https://github.com/DuyKienTTD/Hosting/blob/cbb60147caed49467d76c71b84139e00b4fd3e61/tasks/hosting-post-61.md), [POST-04](https://github.com/DuyKienTTD/Hosting/blob/9d7758b4139e3ce3a2dd26ad7e06413c8c548b6e/reports/2026-11-25-hosting-post-61.md#post-04--đo-read_set).

- Mọi ô gồm `AGENTS.md`, hồ sơ vai trò riêng và đặc tả pin chung. Baseline dùng `agents/chatgpt.md` cho A2, Điều phối, Work. Tám hồ sơ theo thứ tự bảng là `a0-assistant`, `a1`, `a2`, `codex`, `coordinator`, `hermes`, `hostinger`, `work` trong `agents/`.
- C1–C6 đọc toàn Workflow nguyên khối tại baseline, index và các module trong bảng tại hai snapshot sau. MKOE 1–8 là authority, coordination, dispatch, execution, evidence, integrity, handoff, lifecycle. PR #63 dùng các tệp `rules/workflow-<module>.md` và index. Các tệp chuyển tiếp cũ chỉ dùng tra cứu.
- C1/C2/C6 của Trợ lý A0 cộng [tiêu chuẩn pin L35–EOF](https://github.com/DuyKienTTD/Hosting/blob/819249e1c08875f23041502c604c47928bf1bbdc/agents/a0-assistant.md#L35) tại cả ba snapshot. C5 dùng MKOE cùng blob pin cho hai snapshot cũ và blob MKOE đã cập nhật liên kết ở PR #63.
- C2 chỉ review Git và kiểm receipt. Review thêm đặc tả phải cộng dispatch. C4 ghi tài liệu thường và bàn giao, nếu sửa đặc tả/ownership phải cộng dispatch. C5 giả định có quyền ghi trạng thái quản trị riêng. C6 chỉ review KNG. Mọi ca cộng module khi thao tác thật mở rộng, cùng quyết định A0, nguồn live và evidence thuộc phạm vi.
- Định mức cho 56 tổ hợp, không cấp quyền cho từng vai trò. Giả định phiên mới, biết đường dẫn startup, không trừ cache. Chưa đo token, thời gian, chi phí hoặc chất lượng vận hành độc lập.

| Ca POST-04 | Module MKOE | Module PR #63 | Nguồn thêm ngoài Core, role, task và Workflow |
| --- | --- | --- | --- |
| C0 · Khởi đầu | — | — | — |
| C1 · Review phi Git, không ACK | 1, 2, 4, 5, 7 | `common`<br>`review` | — |
| C2 · Review Git + ACK | 1, 2, 3, 4, 5, 6, 7 | `common`<br>`review`<br>`receipts`<br>`git-review` | `rules/REPOSITORY_SECURITY.md`<br>`CONTRIBUTING.md` |
| C3 · Chuẩn bị dispatch ngoài KNG | 1, 2, 3, 4, 5, 7 | `common`<br>`dispatch`<br>`receipts`<br>`handoff`<br>`routing` | `STATE.md` |
| C4 · Ghi Git tài liệu và bàn giao | 1, 2, 3, 4, 5, 6, 7 | `common`<br>`review`<br>`receipts`<br>`git-review`<br>`git-write`<br>`handoff` | `rules/REPOSITORY_SECURITY.md`<br>`CONTRIBUTING.md` |
| C5 · Điều phối + Git + lifecycle + trạng thái | 1, 2, 3, 4, 5, 6, 7, 8 | `common`<br>`review`<br>`dispatch`<br>`receipts`<br>`git-review`<br>`git-write`<br>`handoff`<br>`routing`<br>`lifecycle` | `rules/REPOSITORY_SECURITY.md`<br>`CONTRIBUTING.md`<br>`rules/DATA_LIFECYCLE_CONTEXT.md`<br>`STATE.md`<br>`rules/HOSTING-MKOE-01.md` |
| C6 · Review chỉ định tuyến KNG | 1, 2, 3, 4, 5, 7 | `common`<br>`review`<br>`kng` | `STATE.md`<br>`program/current.json`<br>`program/kng/release_state.py` |

## Bảng 56 ca · Ký tự Unicode

| Vai trò | Ca | 097c080 | c0720d7 | PR #63 | Giảm vs 097c080 | Giảm vs c0720d7 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Trợ lý A0 | C0 | 7787 | 8103 | 8103 | -4.06% | 0.00% |
| Trợ lý A0 | C1 | 30025 | 26778 | 23066 | 23.18% | 13.86% |
| Trợ lý A0 | C2 | 33810 | 35553 | 28928 | 14.44% | 18.63% |
| Trợ lý A0 | C3 | 24513 | 22161 | 19631 | 19.92% | 11.42% |
| Trợ lý A0 | C4 | 23949 | 25692 | 21547 | 10.03% | 16.13% |
| Trợ lý A0 | C5 | 39646 | 43005 | 41876 | -5.62% | 2.63% |
| Trợ lý A0 | C6 | 43550 | 41198 | 35508 | 18.47% | 13.81% |
| A1 | C0 | 6832 | 7138 | 7138 | -4.48% | 0.00% |
| A1 | C1 | 19209 | 15952 | 12240 | 36.28% ✓ | 23.27% |
| A1 | C2 | 22994 | 24727 | 18102 | 21.28% | 26.79% |
| A1 | C3 | 23558 | 21196 | 18666 | 20.77% | 11.94% |
| A1 | C4 | 22994 | 24727 | 20582 | 10.49% | 16.76% |
| A1 | C5 | 38691 | 42040 | 40911 | -5.74% | 2.69% |
| A1 | C6 | 32734 | 30372 | 24682 | 24.60% | 18.73% |
| A2 | C0 | 7050 | 6738 | 6738 | 4.43% | 0.00% |
| A2 | C1 | 19427 | 15552 | 11840 | 39.05% ✓ | 23.87% |
| A2 | C2 | 23212 | 24327 | 17702 | 23.74% | 27.23% |
| A2 | C3 | 23776 | 20796 | 18266 | 23.17% | 12.17% |
| A2 | C4 | 23212 | 24327 | 20182 | 13.05% | 17.04% |
| A2 | C5 | 38909 | 41640 | 40511 | -4.12% | 2.71% |
| A2 | C6 | 32952 | 29972 | 24282 | 26.31% | 18.98% |
| Codex | C0 | 6847 | 7156 | 7156 | -4.51% | 0.00% |
| Codex | C1 | 19224 | 15970 | 12258 | 36.24% ✓ | 23.24% |
| Codex | C2 | 23009 | 24745 | 18120 | 21.25% | 26.77% |
| Codex | C3 | 23573 | 21214 | 18684 | 20.74% | 11.93% |
| Codex | C4 | 23009 | 24745 | 20600 | 10.47% | 16.75% |
| Codex | C5 | 38706 | 42058 | 40929 | -5.74% | 2.68% |
| Codex | C6 | 32749 | 30390 | 24700 | 24.58% | 18.72% |
| Điều phối | C0 | 7050 | 6825 | 6825 | 3.19% | 0.00% |
| Điều phối | C1 | 19427 | 15639 | 11927 | 38.61% ✓ | 23.74% |
| Điều phối | C2 | 23212 | 24414 | 17789 | 23.36% | 27.14% |
| Điều phối | C3 | 23776 | 20883 | 18353 | 22.81% | 12.12% |
| Điều phối | C4 | 23212 | 24414 | 20269 | 12.68% | 16.98% |
| Điều phối | C5 | 38909 | 41727 | 40598 | -4.34% | 2.71% |
| Điều phối | C6 | 32952 | 30059 | 24369 | 26.05% | 18.93% |
| Hermes | C0 | 6813 | 7123 | 7123 | -4.55% | 0.00% |
| Hermes | C1 | 19190 | 15937 | 12225 | 36.29% ✓ | 23.29% |
| Hermes | C2 | 22975 | 24712 | 18087 | 21.28% | 26.81% |
| Hermes | C3 | 23539 | 21181 | 18651 | 20.77% | 11.94% |
| Hermes | C4 | 22975 | 24712 | 20567 | 10.48% | 16.77% |
| Hermes | C5 | 38672 | 42025 | 40896 | -5.75% | 2.69% |
| Hermes | C6 | 32715 | 30357 | 24667 | 24.60% | 18.74% |
| Hostinger Agent | C0 | 6823 | 7136 | 7136 | -4.59% | 0.00% |
| Hostinger Agent | C1 | 19200 | 15950 | 12238 | 36.26% ✓ | 23.27% |
| Hostinger Agent | C2 | 22985 | 24725 | 18100 | 21.25% | 26.79% |
| Hostinger Agent | C3 | 23549 | 21194 | 18664 | 20.74% | 11.94% |
| Hostinger Agent | C4 | 22985 | 24725 | 20580 | 10.46% | 16.76% |
| Hostinger Agent | C5 | 38682 | 42038 | 40909 | -5.76% | 2.69% |
| Hostinger Agent | C6 | 32725 | 30370 | 24680 | 24.58% | 18.74% |
| Work | C0 | 7050 | 6774 | 6774 | 3.91% | 0.00% |
| Work | C1 | 19427 | 15588 | 11876 | 38.87% ✓ | 23.81% |
| Work | C2 | 23212 | 24363 | 17738 | 23.58% | 27.19% |
| Work | C3 | 23776 | 20832 | 18302 | 23.02% | 12.14% |
| Work | C4 | 23212 | 24363 | 20218 | 12.90% | 17.01% |
| Work | C5 | 38909 | 41676 | 40547 | -4.21% | 2.71% |
| Work | C6 | 32952 | 30008 | 24318 | 26.20% | 18.96% |

## Bảng 56 ca · Byte UTF-8

| Vai trò | Ca | 097c080 | c0720d7 | PR #63 | Giảm vs 097c080 | Giảm vs c0720d7 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Trợ lý A0 | C0 | 9315 | 9689 | 9689 | -4.02% | 0.00% |
| Trợ lý A0 | C1 | 36622 | 32084 | 27953 | 23.67% | 12.88% |
| Trợ lý A0 | C2 | 41069 | 42388 | 34783 | 15.31% | 17.94% |
| Trợ lý A0 | C3 | 28639 | 25530 | 22776 | 20.47% | 10.79% |
| Trợ lý A0 | C4 | 28708 | 30027 | 25236 | 12.09% | 15.96% |
| Trợ lý A0 | C5 | 45488 | 49363 | 48164 | -5.88% | 2.43% |
| Trợ lý A0 | C6 | 50181 | 47072 | 40527 | 19.24% | 13.90% |
| A1 | C0 | 8074 | 8438 | 8438 | -4.51% | 0.00% |
| A1 | C1 | 23020 | 18472 | 14341 | 37.70% ✓ | 22.36% |
| A1 | C2 | 27467 | 28776 | 21171 | 22.92% | 26.43% |
| A1 | C3 | 27398 | 24279 | 21525 | 21.44% | 11.34% |
| A1 | C4 | 27467 | 28776 | 23985 | 12.68% | 16.65% |
| A1 | C5 | 44247 | 48112 | 46913 | -6.03% | 2.49% |
| A1 | C6 | 36579 | 33460 | 26915 | 26.42% | 19.56% |
| A2 | C0 | 8334 | 7951 | 7951 | 4.60% | 0.00% |
| A2 | C1 | 23280 | 17985 | 13854 | 40.49% ✓ | 22.97% |
| A2 | C2 | 27727 | 28289 | 20684 | 25.40% | 26.88% |
| A2 | C3 | 27658 | 23792 | 21038 | 23.94% | 11.58% |
| A2 | C4 | 27727 | 28289 | 23498 | 15.25% | 16.94% |
| A2 | C5 | 44507 | 47625 | 46426 | -4.31% | 2.52% |
| A2 | C6 | 36839 | 32973 | 26428 | 28.26% | 19.85% |
| Codex | C0 | 8103 | 8470 | 8470 | -4.53% | 0.00% |
| Codex | C1 | 23049 | 18504 | 14373 | 37.64% ✓ | 22.32% |
| Codex | C2 | 27496 | 28808 | 21203 | 22.89% | 26.40% |
| Codex | C3 | 27427 | 24311 | 21557 | 21.40% | 11.33% |
| Codex | C4 | 27496 | 28808 | 24017 | 12.65% | 16.63% |
| Codex | C5 | 44276 | 48144 | 46945 | -6.03% | 2.49% |
| Codex | C6 | 36608 | 33492 | 26947 | 26.39% | 19.54% |
| Điều phối | C0 | 8334 | 8048 | 8048 | 3.43% | 0.00% |
| Điều phối | C1 | 23280 | 18082 | 13951 | 40.07% ✓ | 22.85% |
| Điều phối | C2 | 27727 | 28386 | 20781 | 25.05% | 26.79% |
| Điều phối | C3 | 27658 | 23889 | 21135 | 23.58% | 11.53% |
| Điều phối | C4 | 27727 | 28386 | 23595 | 14.90% | 16.88% |
| Điều phối | C5 | 44507 | 47722 | 46523 | -4.53% | 2.51% |
| Điều phối | C6 | 36839 | 33070 | 26525 | 28.00% | 19.79% |
| Hermes | C0 | 8044 | 8412 | 8412 | -4.57% | 0.00% |
| Hermes | C1 | 22990 | 18446 | 14315 | 37.73% ✓ | 22.40% |
| Hermes | C2 | 27437 | 28750 | 21145 | 22.93% | 26.45% |
| Hermes | C3 | 27368 | 24253 | 21499 | 21.44% | 11.36% |
| Hermes | C4 | 27437 | 28750 | 23959 | 12.68% | 16.66% |
| Hermes | C5 | 44217 | 48086 | 46887 | -6.04% | 2.49% |
| Hermes | C6 | 36549 | 33434 | 26889 | 26.43% | 19.58% |
| Hostinger Agent | C0 | 8073 | 8444 | 8444 | -4.60% | 0.00% |
| Hostinger Agent | C1 | 23019 | 18478 | 14347 | 37.67% ✓ | 22.36% |
| Hostinger Agent | C2 | 27466 | 28782 | 21177 | 22.90% | 26.42% |
| Hostinger Agent | C3 | 27397 | 24285 | 21531 | 21.41% | 11.34% |
| Hostinger Agent | C4 | 27466 | 28782 | 23991 | 12.65% | 16.65% |
| Hostinger Agent | C5 | 44246 | 48118 | 46919 | -6.04% | 2.49% |
| Hostinger Agent | C6 | 36578 | 33466 | 26921 | 26.40% | 19.56% |
| Work | C0 | 8334 | 7988 | 7988 | 4.15% | 0.00% |
| Work | C1 | 23280 | 18022 | 13891 | 40.33% ✓ | 22.92% |
| Work | C2 | 27727 | 28326 | 20721 | 25.27% | 26.85% |
| Work | C3 | 27658 | 23829 | 21075 | 23.80% | 11.56% |
| Work | C4 | 27727 | 28326 | 23535 | 15.12% | 16.91% |
| Work | C5 | 44507 | 47662 | 46463 | -4.39% | 2.52% |
| Work | C6 | 36839 | 33010 | 26465 | 28.16% | 19.83% |

## Manifest blob theo nguồn

| Phiên bản | Path hoặc range | SHA blob Git | Unicode | UTF-8 byte |
| --- | --- | --- | ---: | ---: |
| 097c080 | `AGENTS.md` | `323725dc632b08a35da6e5d4fd08de30a8604978` | 3534 | 4296 |
| 097c080 | `CONTRIBUTING.md` | `02ce8d779a4d9645045d869eba1f005abc83c965` | 2645 | 3137 |
| 097c080 | `STATE.md` | `519160e28f833ee2edfc38e8f64f0ced898d6039` | 4349 | 4378 |
| 097c080 | `agents/a0-assistant.md` | `21e11fe6f2562074b1fd1cabb09383d668334145` | 1561 | 1925 |
| 097c080 | `agents/a1.md` | `e2d68f988da019d1161776968b4bc98f8a90c7f1` | 606 | 684 |
| 097c080 | `agents/chatgpt.md` | `85281a11a3bd979bf017679493592f1d376fa50c` | 824 | 944 |
| 097c080 | `agents/codex.md` | `1a752639a1c09f6b7ba06034e29bb5fa783ac827` | 621 | 713 |
| 097c080 | `agents/hermes.md` | `0ab858418f77f3d69a00d271445350d82313c208` | 587 | 654 |
| 097c080 | `agents/hostinger.md` | `f2f444a7acecfecb3f909086a2042d6a3e6209a6` | 597 | 683 |
| 097c080 | `program/current.json` | `f4cfc3fde6140077c7dd01431ce82f14a9d37c65` | 4101 | 4106 |
| 097c080 | `program/kng/release_state.py` | `ae9d31bb3d7b3b88b785b31771cb049e6e161799` | 5075 | 5075 |
| 097c080 | `rules/AGENT_WORKFLOW.md` | `c6249467818e5bae64b30b0ebbaef04b6b2fd11d` | 12377 | 14946 |
| 097c080 | `rules/DATA_LIFECYCLE_CONTEXT.md` | `06652e337753daa2e12e3635d1fbaa313d91e3df` | 6007 | 7054 |
| 097c080 | `rules/REPOSITORY_SECURITY.md` | `c24d608036b11dcd3fafcaefbefa23fdb591990e` | 1140 | 1310 |
| c0720d7 | `AGENTS.md` | `e41c77133451c1f527fe2f3f306c14d8acdaff14` | 3648 | 4415 |
| c0720d7 | `CONTRIBUTING.md` | `02ce8d779a4d9645045d869eba1f005abc83c965` | 2645 | 3137 |
| c0720d7 | `STATE.md` | `017df6ec4e8cb27ff0f05c0645ee5e65a8e87504` | 2258 | 2265 |
| c0720d7 | `agents/a0-assistant.md` | `fc980af86aefe219a97325bf116f76d24bedab33` | 1763 | 2180 |
| c0720d7 | `agents/a1.md` | `9af03b802f99bfeeec6b8ae9c6b323d2ace4857a` | 798 | 929 |
| c0720d7 | `agents/a2.md` | `ea1185004364287f69c7a2f9a60f08b77aa25b3c` | 398 | 442 |
| c0720d7 | `agents/codex.md` | `8a65dd3704c7f9e282c1eb59062c3828a2afae1c` | 816 | 961 |
| c0720d7 | `agents/coordinator.md` | `23fe5abd215aba542b34410288418e1952a1191f` | 485 | 539 |
| c0720d7 | `agents/hermes.md` | `98801e4a6f68bbe4a874bd4c27938cde0c4172ec` | 783 | 903 |
| c0720d7 | `agents/hostinger.md` | `7d8797e651615f51f76f8dca37403e9876bffe9d` | 796 | 935 |
| c0720d7 | `agents/work.md` | `7e50048558a4028d5babf2c8155283b32b50be7b` | 434 | 479 |
| c0720d7 | `program/current.json` | `f4cfc3fde6140077c7dd01431ce82f14a9d37c65` | 4101 | 4106 |
| c0720d7 | `program/kng/release_state.py` | `ae9d31bb3d7b3b88b785b31771cb049e6e161799` | 5075 | 5075 |
| c0720d7 | `rules/AGENT_WORKFLOW.md` | `e803f41ab917c657e25af236cc622e9f034cab2c` | 1523 | 1576 |
| c0720d7 | `rules/DATA_LIFECYCLE_CONTEXT.md` | `06652e337753daa2e12e3635d1fbaa313d91e3df` | 6007 | 7054 |
| c0720d7 | `rules/HOSTING-MKOE-01.md` | `3cfc5b3de4ac97f233d5b1acc7bf1bff5ed29acc` | 5341 | 5348 |
| c0720d7 | `rules/REPOSITORY_SECURITY.md` | `c24d608036b11dcd3fafcaefbefa23fdb591990e` | 1140 | 1310 |
| c0720d7 | `rules/authority.md` | `879996b2b0432b2284d698fd0b9e8c0a20ec1f2d` | 936 | 1082 |
| c0720d7 | `rules/coordination.md` | `8301aecf815773394e5f75d0110623b7e1bcec91` | 2275 | 2607 |
| c0720d7 | `rules/dispatch.md` | `31608f8263f663ea33caf641a50e5eee14f87416` | 2986 | 3542 |
| c0720d7 | `rules/evidence.md` | `510b7fecf342a67de3bb8a65817bb0584c6d534d` | 1086 | 1233 |
| c0720d7 | `rules/execution.md` | `30a24042e3076327248724347c1f235436ae79df` | 1878 | 2248 |
| c0720d7 | `rules/handoff.md` | `9f3ef905f7610f40736a6b50f1c9d21938668857` | 1116 | 1288 |
| c0720d7 | `rules/integrity.md` | `a8e466e54cf37312a4add6237879ce3b7b7b8b0b` | 2004 | 2315 |
| c0720d7 | `rules/lifecycle.md` | `6372d3f9356e34c462a494c277bae630d2ee6c12` | 3707 | 4669 |
| PR #63 | `AGENTS.md` | `e41c77133451c1f527fe2f3f306c14d8acdaff14` | 3648 | 4415 |
| PR #63 | `CONTRIBUTING.md` | `501908e880ec299f6668f1c8d5b5095f9090ee6a` | 2656 | 3152 |
| PR #63 | `STATE.md` | `017df6ec4e8cb27ff0f05c0645ee5e65a8e87504` | 2258 | 2265 |
| PR #63 | `agents/a0-assistant.md` | `fc980af86aefe219a97325bf116f76d24bedab33` | 1763 | 2180 |
| PR #63 | `agents/a1.md` | `9af03b802f99bfeeec6b8ae9c6b323d2ace4857a` | 798 | 929 |
| PR #63 | `agents/a2.md` | `ea1185004364287f69c7a2f9a60f08b77aa25b3c` | 398 | 442 |
| PR #63 | `agents/codex.md` | `8a65dd3704c7f9e282c1eb59062c3828a2afae1c` | 816 | 961 |
| PR #63 | `agents/coordinator.md` | `23fe5abd215aba542b34410288418e1952a1191f` | 485 | 539 |
| PR #63 | `agents/hermes.md` | `98801e4a6f68bbe4a874bd4c27938cde0c4172ec` | 783 | 903 |
| PR #63 | `agents/hostinger.md` | `7d8797e651615f51f76f8dca37403e9876bffe9d` | 796 | 935 |
| PR #63 | `agents/work.md` | `7e50048558a4028d5babf2c8155283b32b50be7b` | 434 | 479 |
| PR #63 | `program/current.json` | `f4cfc3fde6140077c7dd01431ce82f14a9d37c65` | 4101 | 4106 |
| PR #63 | `program/kng/release_state.py` | `ae9d31bb3d7b3b88b785b31771cb049e6e161799` | 5075 | 5075 |
| PR #63 | `rules/AGENT_WORKFLOW.md` | `26a137aaa2d5f5b7140e7951c42f4d6995d8fdfb` | 1956 | 2184 |
| PR #63 | `rules/DATA_LIFECYCLE_CONTEXT.md` | `06652e337753daa2e12e3635d1fbaa313d91e3df` | 6007 | 7054 |
| PR #63 | `rules/HOSTING-MKOE-01.md` | `b4b73fd064df07f0abb9cee9761d70b09681382f` | 5420 | 5427 |
| PR #63 | `rules/REPOSITORY_SECURITY.md` | `c24d608036b11dcd3fafcaefbefa23fdb591990e` | 1140 | 1310 |
| PR #63 | `rules/workflow-common.md` | `88c7105cb15d0810b388ee1d092e67471e3860df` | 2129 | 2557 |
| PR #63 | `rules/workflow-dispatch.md` | `b3e5430890d192ad96ce91a50e3050bf6e664c20` | 2281 | 2748 |
| PR #63 | `rules/workflow-git-review.md` | `07631cde8a0a613074b3f42897d757c5e59e6222` | 1224 | 1397 |
| PR #63 | `rules/workflow-git-write.md` | `d50f78b74ca6476e7d9ccee1142afa41eb0e0b46` | 1164 | 1311 |
| PR #63 | `rules/workflow-handoff.md` | `eb688df46d5a0d108156e36e24062af2df7033ff` | 1316 | 1503 |
| PR #63 | `rules/workflow-kng.md` | `b5aa41f42cb769adc7ac7a154874dd46887dc60c` | 1008 | 1128 |
| PR #63 | `rules/workflow-lifecycle.md` | `96ec0451afcc5ac064ac84c6ba2484c5aa15c78a` | 3617 | 4575 |
| PR #63 | `rules/workflow-receipts.md` | `d297a88125cf0c2d275af2e9b51177a0c2dab7c9` | 842 | 971 |
| PR #63 | `rules/workflow-review.md` | `39c041518aff120b0e2ec0284fd7de45891b6e2f` | 1017 | 1162 |
| PR #63 | `rules/workflow-routing.md` | `f3ccf68f78a12e4a017b4e60d68d6f316f4e8859` | 746 | 859 |
| cbb6014 | `tasks/hosting-post-61.md` | `d4a018e149fdd614d773f86db0a200690bae11cd` | 2692 | 3094 |
| 819249e | `agents/a0-assistant.md` L35–EOF | `eaed4d33e3862d9a08a476bc288e7123431bbf25` | 9861 | 12361 |
