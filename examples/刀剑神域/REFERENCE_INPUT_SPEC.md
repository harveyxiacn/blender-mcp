# SAO 角色参考图输入规范（桐人 / 亚丝娜）

把你的同人图和手办图放到：

`examples/刀剑神域/references/`

按下面命名即可，我会直接用这些图做下一轮 MCP 精修。

## 1. 桐人 Kirito

- `kirito_front.*`：正面全身
- `kirito_side.*`：侧面全身（左或右都可）
- `kirito_back.*`：背面全身
- `kirito_face_close.*`：脸部特写（眼睛、发型）
- `kirito_coat_detail.*`：风衣细节（镶边、扣件）
- `kirito_weapon_elucidator.*`：逐暗者细节（护手、握把）
- `kirito_pose_ref.*`：动作参考（战斗姿态）

## 2. 亚丝娜 Asuna

- `asuna_front.*`：正面全身
- `asuna_side.*`：侧面全身
- `asuna_back.*`：背面全身
- `asuna_face_close.*`：脸部特写（眼睛、刘海）
- `asuna_hair_detail.*`：长发和辫子结构
- `asuna_kob_outfit_detail.*`：KoB 服装细节（胸甲十字、肩甲、裙摆）
- `asuna_weapon_lambentlight.*`：闪光细剑细节
- `asuna_pose_ref.*`：动作参考（刺击姿态）

## 3. 手办图（强烈建议）

- `figure_kirito_front.*`
- `figure_kirito_side.*`
- `figure_asuna_front.*`
- `figure_asuna_side.*`

## 4. 图片要求

- 分辨率建议 `>= 1200px`（长边）
- 尽量无遮挡、透视不过强
- 同一个角色尽量同一版本服装
- 文件格式：`jpg/png/webp` 都可以

## 5. 交付后我会做的事

- 用 MCP 自动比对当前模型与参考图
- 调整头身比例、发束、服装结构和武器轮廓
- 细化动作关键帧（桐人斩击 + 亚丝娜刺击）
- 输出新文件：
  - `examples/sao_kirito_asuna_action_refined.blend`
  - `examples/sao_kirito_asuna_action_refined_f24.png`

