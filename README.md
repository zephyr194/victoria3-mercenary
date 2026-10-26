# Victoria 3 Mercenary · 开发版

面向 Victoria 3 1.13 / 1.14-openbeta 的雇佣兵模组。当前版本 **0.1.0-dev：合同系统与免费沙盒**，尚未提供可部署的雇佣兵。

## 当前可做什么

- 在玩家国家的日志中打开“雇佣兵事务（开发预览）”。
- 选择 Lv.1 / Lv.2 / Lv.3、5 / 10 营的模拟合同。
- 演练四周集结、52 周服役、入场费、每周账单、欠薪、续约、解约、撤离与八周休整。
- 用独立模拟余额观察账单；**不扣真实国库、不生成部队、不影响战斗属性**。
- 正式雇佣入口被能力检查锁定，不能购买没有交付的兵力。

这是上一轮方案的第一阶段实现，不是完整雇佣兵系统。等级目前参与报价，尚无战斗效果；外籍人口、区域市场、成长与 AI 招募未实现。

## 本地验证与打包

需要 Python 3.10+，无第三方依赖：

```sh
python3 -m unittest discover -s tests -v
python3 tools/validate.py
python3 scripts/package.py --target 1.13 --experimental
python3 scripts/package.py --target 1.14 --experimental
```

把 zip 中 `mc_mercenary.mod` 和 `mc_mercenary/` 一起解压到用户的 `Victoria 3/mod/` 目录，再在启动器中启用。不要放进游戏安装目录。包内描述符声明目标版本，不表示已通过实机兼容测试。

## 为什么正式雇佣尚未开放

已核查的版本引擎文档有创建军队和增减国库接口，但没有证明可以安全地识别、独立补员和清退一个临时陆军合同的全部单位。创建军队时直接使用普通兵营，再在到期时删除兵营，会有破坏正规军的风险。

本项目因此不使用全国战斗加成代替佣兵，也不自动删除普通兵营。实际部队后端需要完成 [军事验证清单](docs/MILITARY_BACKEND.md)，才能打开正式入口。

- [设计与已实现范围](docs/DESIGN.zh-CN.md)
- [实机测试步骤](docs/INSTALL_TEST.zh-CN.md)
- [接口证据](docs/SOURCES.md)
- [兼容状态](compatibility.json)

脚本使用 `mc_` 前缀；不覆盖原版定义，不依赖驻军模组。`tests/script_runtime.py` 是执行本仓库合同脚本子集的测试工具，**不是游戏引擎**。
