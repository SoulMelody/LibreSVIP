| 格式后缀         | 适用引擎/软件                        | 基本类型     | 类型说明                            | 备注                              | 开发状态 |
| ------------ | ------------------------------ | -------- | ------------------------------- | ------------------------------- | ---- |
| `acep`         | ACE Studio                     | 标准序列化格式  | 基于json；内容使用了zstandard压缩         | 公测期间曾更换过加密方法，最终于1.7.8版本移除       | 活跃开发 |
| `ais`          | AISingers Web                  | 混合类型     | 将json头和自定义文本拼接而成                |                                 | 暂停维护 |
| `aisp`         | AISingers Studio               | 混合类型     | 基于json；为两段json拼接而成              |                                 | 尚在维护 |
| `ccs/ccst`     | CeVIO Creative Studio          | 标准序列化格式  | 基于xml                           |                                 | 活跃开发 |
| `ds`           | DiffSinger                     | 标准序列化格式  | 基于json                          | 为临时解决方案                         | 活跃开发 |
| `dsc`          | 大市唱                         | 标准序列化格式  | 基于json                          |                                 | 活跃开发 |
| `dspx`         | DiffScope                      | 标准序列化格式  | 基于json                          | 尚在开发中                           | 活跃开发 |
| `dv/sk`        | DeepVocal/Sharpkey             | 自定义二进制格式 |                                 |                                 | 疑似暂停 |
| `gj`           | 歌叽歌叽                           | 标准序列化格式  | 基于json                          |                                 | 停止开发 |
| `json`         | OpenSVIP                       | 标准序列化格式  | 基于json                          |                                 | 尚在维护 |
| `nn`           | 袅袅虚拟歌手                         | 自定义文本格式  |                                 |                                 | 停止开发 |
| `mid/midi`     | 众多音序器/DAW                      | 标准二进制格式  | 标准MIDI(SMF)格式                   |                                 | 尚在维护 |
| `mtp`          | MUTA 2                         | 自定义二进制格式 |                                 |                                 | 停止开发 |
| `MusicXML`     | MuseScore、Sibelius、Finale等打谱软件 | 标准序列化格式  | 基于xml                           |                                 | 活跃开发 |
| `ppsf`         | Piapro Studio                  | 混合类型     | 旧版使用自定义二进制格式；NT版基于json，并使用zip压缩 |                                 | 尚在维护 |
| `ps_project`   | Pocket Singer                  | 标准序列化格式  | 基于json，并使用zip压缩                 | 需要解压密码                          | 活跃开发 |
| `s5p`          | Synthesizer V Editor           | 标准序列化格式  | 基于json                          |                                 | 停止开发 |
| `svip`         | X Studio Singer 1/2            | 标准二进制格式  | 基于.net framework的MS-NRBF格式      | 已过时                             | 停止开发 |
| `svip3`        | X Studio 3/网易云音乐·X Studio      | 标准二进制格式  | 基于protobuf                      |                                 | 活跃开发 |
| `svp`          | Synthesizer V Studio           | 标准序列化格式  | 基于json                          |                                 | 活跃开发 |
| `tlp`          | TuneLab                        | 标准序列化格式  | 基于json                          |                                 | 活跃开发 |
| `tssln/tssprj` | VoiSona                        | 自定义二进制格式 | 基于JUCE框架的ValueTree数据结构          |                                 | 活跃开发 |
| `tsmsln`       | VoiSona Mobile                 | 自定义二进制格式 | 基于JUCE框架的ValueTree数据结构          |                                 | 活跃开发 |
| `ufdata`       | UtaFormatix 3                  | 标准序列化格式  | 基于json                          |                                 | 活跃开发 |
| `ust`          | Ameya UTAU                     | 自定义文本格式  |                                 |                                 | 尚在维护 |
| `ustx`         | OpenUTAU                       | 标准序列化格式  | 基于yaml                          |                                 | 活跃开发 |
| `vcp`          | Cantor 2                    | 自定义二进制格式  |                  |                                 | 停止开发 |
| `vfp`          | VOX Factory                    | 标准序列化格式  | 基于json，并使用zip压缩                 |                                 | 活跃开发 |
| `vog`          | Vogen                          | 标准序列化格式  | 基于json，并使用zip压缩                 |                                 | 疑似暂停 |
| `vpr`          | Vocaloid 5+                    | 标准序列化格式  | 基于json，并使用zip压缩                 |                                 | 活跃开发 |
| `vsp`          | Vocalina Studio                | 自定义二进制格式 |                                 |                                 | 停止开发 |
| `vspx`         | VocalSharp                     | 标准序列化格式  | 基于xml                           | 使用了自定义的序列化和解析框架，在生成vspx文件时需特殊处理 | 停止开发 |
| `vsq`          | Vocaloid 2                     | 自定义二进制格式 | 基于MIDI和INI                      |                                 | 停止开发 |
| `vsqx`         | Vocaloid 3/4                   | 标准序列化格式  | 基于xml                           |                                 | 尚在维护 |
| `vvproj`       | VOICEVOX                       | 标准序列化格式  | 基于json                          |                                 | 活跃开发 |
| `vxf`          | VOCALOID β-STUDIO              | 自定义二进制格式 | 基于MIDI2.0切片(SMF2CLIP)格式                   |                                 | 活跃开发 |
| `xvsq`         | Cadencii                   | 标准序列化格式  | 基于xml                           |                                 | 停止开发 |
| `y77`          | 元七七编辑器                       | 标准序列化格式  | 基于json                          |                                 | 停止开发 |
