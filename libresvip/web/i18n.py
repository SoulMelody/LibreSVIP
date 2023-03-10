from trame_server.core import Server


def initialize(server: Server):
    state = server.state
    state.translations = {
        "简体中文": {
            "简体中文": "简体中文",
            "English": "英语",
            "LibreSVIP": "歌声合成工程文件转换器",
            "Convert": "转换",
            "Visualize": "可视化",
            "Plugins": "插件",
            "Settings": "设置",
            "About": "关于",
            "Help": "帮助",
            "Links": "链接",
            "Export": "导出",
            "Switch Theme": "切换主题",
            "Switch Language": "切换语言",
            "OK": "确定",
            "Close": "关闭",
            "Author": "作者",
            "Version": "版本",
            "Introduction": "简介",
            "Auto detect import format": "自动检测导入格式",
            "Reset list when import format changed": "切换格式时重置列表",
            "Import from": "导入自",
            "Import format": "导入工程格式",
            "Export to": "导出至",
            "Export format": "导出工程格式",
            "Choose file format": "选择格式",
            "Next": "继续",
            "Back": "返回",
            "File operations": "文件操作",
            "Import project": "导入工程",
            "Import Options": "导入选项",
            "Export Options": "导出选项",
            "Advanced Options": "高级选项",
            "Conversion Successful": "转换成功",
            "Conversion Failed": "转换失败",
            "Drag and drop files here or click to upload": "拖放文件或点击导入",
            "About Text 1": "LibreSVIP 是一个开源、开放、插件化的歌声合成工程文件中介与转换平台。",
            "About Text 2": "所有人都应享有选择的权利和自由。因此，我们致力于为您带来第二次机会，使您的创作免受平台的制约与圈子的束缚。",
            "Plugins List": "插件列表",
            "Install a Plugin": "安装插件",
        },
        "English": {
            "简体中文": "Simplified Chinese",
            "English": "English",
            "LibreSVIP": "LibreSVIP",
            "Convert": "Convert",
            "Visualize": "Visualize",
            "Plugins": "Plugins",
            "Settings": "Settings",
            "About": "About",
            "Help": "Help",
            "Links": "Links",
            "Export": "Export",
            "Switch Theme": "Switch Theme",
            "Switch Language": "Switch Language",
            "OK": "OK",
            "Close": "Close",
            "Author": "Author",
            "Version": "Version",
            "Introduction": "Introduction",
            "Next": "Next",
            "Back": "Back",
            "File operations": "File operations",
            "Auto detect import format": "Auto detect import format",
            "Reset list when import format changed": "Reset list when import format changed",
            "Import project": "Import project",
            "Import from": "Import from",
            "Import format": "Import format",
            "Export to": "Export to",
            "Export format": "Export format",
            "Choose file format": "Choose file format",
            "Import Options": "Import Options",
            "Export Options": "Export Options",
            "Advanced Options": "Advanced Options",
            "Conversion Successful": "Conversion Successful",
            "Conversion Failed": "Conversion Failed",
            "Drag and drop files here or click to upload": "Drag and drop files here or click to upload",
            "About Text 1": "",
            "About Text 2": "",
            "Plugins List": "Plugins List",
            "Install a Plugin": "Install a Plugin",
        },
    }
