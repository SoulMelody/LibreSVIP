## 是否支持Vocaloid1 MIDI格式?

Vocaloid1 MIDI格式在具体内容方面与Vocaloid2的vsq格式基本一致，主要区别只是文件后缀不同。因此，实际上也是可以支持的，只是需要几项手动调整的步骤。

在导入时，可以关闭"切换格式时重置列表"及"自动检测导入格式"两个开关，再手动选择导入格式为vsq格式；在导出时，可以关闭"自动设置后缀名"这个开关，再选择导出格式为vsq格式，最后给导出文件名末尾加入.mid后缀。

## 是否支持Vocaloid版Piapro Studio的工程格式(.ppsf)?

因为Vocaloid版本的ppsf格式属于自定义二进制格式(详见 <a class="external" href="/LibreSVIP/project_formats/">歌声合成工程格式一览</a>)，并且Crypton Future Media官方也没有提供文档供解析，因此仅提供基本的导入支持。而Piapro Studio编辑器支持vsqx格式的导入/导出，建议以vsqx格式作为中介。