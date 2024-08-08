## V2.0

- 文档更新：
    - README新增层级架构描述。
- 性能优化：
    - 提升代码架构性能。
- 代码重构：
    - 检查和改进路由代码
    - 优化资源属性处理。
- 日志增强：
    - 记录HTTP请求来源
    - 调整API错误日志级别。
- 错误修复：
    - 处理重启后的加载错误
    - 避免P块重复加载。
- 功能添加：
    - 实现思源信息同步推送。
- 其他改进：
    - 优化日志提示
    - 修正打字错误。

### commit log

- fix:
  - [record loading error after reboot](https://github.com/M2uyo/Siyuan_pic_bed/commit/cf2d28cf8280f16f9fb9943e021b35aa0e64b8d5)
  - [repeatedly loading p blocks](https://github.com/M2uyo/Siyuan_pic_bed/commit/83a86eb524410eee3d9d66ded361a74f03d6d262)
- feat:
  - [add synchronized siyuan information push method](https://github.com/M2uyo/Siyuan_pic_bed/commit/d52f1c26f2301709ec42dfdec74ab923460015f9)
- perf:
  - [optimize code architecture](https://github.com/M2uyo/Siyuan_pic_bed/commit/ebf25ea10289ca201daa4e17085be7bec2fc8a80)
- refactor:
  - [check router](https://github.com/M2uyo/Siyuan_pic_bed/commit/e1f80857faeabee9b3fe22ac11d61580804a3994)
  - [raise the file attribute of the corresponding resource as an instance attribute](https://github.com/M2uyo/Siyuan_pic_bed/commit/0e2a1b164d231b15676f9aae762f7977f243ea38)
  - [obtain filename method](https://github.com/M2uyo/Siyuan_pic_bed/commit/2d5cec33ba09b7f0a7deb8097ac80da58e8da836)
  - [change the return value judgment of 123 cloud](https://github.com/M2uyo/Siyuan_pic_bed/commit/fe9c2b543b985c8cb1c5e716a8573c2d8371f46b)
  - [resource_dict filed name](https://github.com/M2uyo/Siyuan_pic_bed/commit/a01813322956aabf83d3f16d5ef8bfe49aff11d9)
  - [field name (provider changed field name)](https://github.com/M2uyo/Siyuan_pic_bed/commit/2aafdd424fa4ad4e6863d9c1c25ff5fd068aa49a)
  - ['-' -> setting.num_tag](https://github.com/M2uyo/Siyuan_pic_bed/commit/fb9d4647b1188b080de3a1a7abf35d28bf24bbed)
- optimize:
  - [log prompts](https://github.com/M2uyo/Siyuan_pic_bed/commit/288ec1bf83e6d79cf64005392f3556ac9105ff12)
- log:
  - [add http request source](https://github.com/M2uyo/Siyuan_pic_bed/commit/fe4fbad3f6daba1f282346e9171ff096d1386b6d)
- style:
  - [change the log level of api errors](https://github.com/M2uyo/Siyuan_pic_bed/commit/bd52e2280e7a7b8124714de1045fcf394784726e)
  - [typo](https://github.com/M2uyo/Siyuan_pic_bed/commit/c16de7a87a76892d6f0ad175e425685aa1f66e65)
- readme:
  - [hierarchical architecture](https://github.com/M2uyo/Siyuan_pic_bed/commit/6c1ce998806c6bc6c77fcbcb0c175e0e017affac)
