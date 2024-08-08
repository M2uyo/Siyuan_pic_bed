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
    - record loading error after reboot
    - repeatedly loading p blocks
- feat:
    - add synchronized siyuan information push method
- perf:
    - optimize code architecture
- refactor:
    - check router
    - raise the file attribute of the corresponding resource as an instance attribute
    - obtain filename method
    - change the return value judgment of 123 cloud
    - resource_dict filed name
    - field name (provider changed field name)
    - '-' -> setting.num_tag
- optimize:
    - log prompts
- log:
    - add http request source
- style:
    - change the log level of api errors
    - typo
- readme:
    - hierarchical architecture 
