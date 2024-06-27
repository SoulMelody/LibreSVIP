import itertools
from functools import cached_property
from typing import Optional

from pydantic import BaseModel
from xsdata_pydantic.fields import field

__NAMESPACE__ = "https://mediaarea.net/mediainfo"


class Creation(BaseModel):
    class Meta:
        name = "creation"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    version: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    url: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    build_date: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    build_time: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    compiler_ident: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Track(BaseModel):
    class Meta:
        name = "track"

    accompaniment: Optional[str] = field(
        default=None,
        metadata={
            "name": "Accompaniment",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    active_format_description: Optional[str] = field(
        default=None,
        metadata={
            "name": "ActiveFormatDescription",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    actor: Optional[str] = field(
        default=None,
        metadata={
            "name": "Actor",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    actor_character: Optional[str] = field(
        default=None,
        metadata={
            "name": "Actor_Character",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    added_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "Added_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    album: Optional[str] = field(
        default=None,
        metadata={
            "name": "Album",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    album_more: Optional[str] = field(
        default=None,
        metadata={
            "name": "Album_More",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    album_performer: Optional[str] = field(
        default=None,
        metadata={
            "name": "Album_Performer",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    album_performer_sort: Optional[str] = field(
        default=None,
        metadata={
            "name": "Album_Performer_Sort",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    album_replay_gain_gain: Optional[str] = field(
        default=None,
        metadata={
            "name": "Album_ReplayGain_Gain",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    album_replay_gain_peak: Optional[str] = field(
        default=None,
        metadata={
            "name": "Album_ReplayGain_Peak",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    active_display_aspect_ratio: Optional[float] = field(
        default=None,
        metadata={
            "name": "Active_DisplayAspectRatio",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    active_height: Optional[int] = field(
        default=None,
        metadata={
            "name": "Active_Height",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    active_width: Optional[int] = field(
        default=None,
        metadata={
            "name": "Active_Width",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    active_format_description_muxing_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "ActiveFormatDescription_MuxingMode",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    active_format_description_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "ActiveFormatDescription_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    album_performer_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "Album_Performer_Url",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    album_replay_gain_gain_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Album_ReplayGain_Gain_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    album_sort: Optional[str] = field(
        default=None,
        metadata={
            "name": "Album_Sort",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    alignment: Optional[str] = field(
        default=None,
        metadata={
            "name": "Alignment",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    alignment_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Alignment_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    alternate_group: Optional[str] = field(
        default=None,
        metadata={
            "name": "AlternateGroup",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    alternate_group_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "AlternateGroup_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    archival_location: Optional[str] = field(
        default=None,
        metadata={
            "name": "Archival_Location",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    arranger: Optional[str] = field(
        default=None,
        metadata={
            "name": "Arranger",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    art_director: Optional[str] = field(
        default=None,
        metadata={
            "name": "ArtDirector",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    assistant_director: Optional[str] = field(
        default=None,
        metadata={
            "name": "AssistantDirector",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    audio_codec_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Audio_Codec_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    audio_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "AudioCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    audio_channels_total: Optional[int] = field(
        default=None,
        metadata={
            "name": "Audio_Channels_Total",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    audio_format_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Audio_Format_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    audio_format_with_hint_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Audio_Format_WithHint_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    audio_language_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Audio_Language_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bar_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "BarCode",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_depth_detected: Optional[int] = field(
        default=None,
        metadata={
            "name": "BitDepth_Detected",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_depth_detected_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "BitDepth_Detected_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_depth: Optional[int] = field(
        default=None,
        metadata={
            "name": "BitDepth",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_depth_stored: Optional[int] = field(
        default=None,
        metadata={
            "name": "BitDepth_Stored",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_depth_stored_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "BitDepth_Stored_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_depth_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "BitDepth_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_rate_encoded: Optional[float] = field(
        default=None,
        metadata={
            "name": "BitRate_Encoded",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_rate_encoded_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "BitRate_Encoded_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_rate_maximum: Optional[float] = field(
        default=None,
        metadata={
            "name": "BitRate_Maximum",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_rate_maximum_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "BitRate_Maximum_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_rate_minimum: Optional[float] = field(
        default=None,
        metadata={
            "name": "BitRate_Minimum",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_rate_minimum_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "BitRate_Minimum_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_rate: Optional[float] = field(
        default=None,
        metadata={
            "name": "BitRate",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_rate_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "BitRate_Mode",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_rate_mode_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "BitRate_Mode_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_rate_nominal: Optional[float] = field(
        default=None,
        metadata={
            "name": "BitRate_Nominal",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_rate_nominal_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "BitRate_Nominal_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bit_rate_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "BitRate_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bits_pixel_frame: Optional[float] = field(
        default=None,
        metadata={
            "name": "Bits-Pixel_Frame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mediaarea_net_mediainfo_bits_pixel_frame: Optional[float] = field(
        default=None,
        metadata={
            "name": "BitsPixel_Frame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    bpm: Optional[str] = field(
        default=None,
        metadata={
            "name": "BPM",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    buffer_size: Optional[str] = field(
        default=None,
        metadata={
            "name": "BufferSize",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    catalog_number: Optional[str] = field(
        default=None,
        metadata={
            "name": "CatalogNumber",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    channel_layout_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ChannelLayoutID",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    channel_layout: Optional[str] = field(
        default=None,
        metadata={
            "name": "ChannelLayout",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    channel_layout_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "ChannelLayout_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    channel_positions: Optional[str] = field(
        default=None,
        metadata={
            "name": "ChannelPositions",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    channel_positions_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "ChannelPositions_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    channel_positions_original_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "ChannelPositions_Original_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    channel_positions_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "ChannelPositions_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    channel_s: Optional[int] = field(
        default=None,
        metadata={
            "name": "Channels",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    channels_original: Optional[int] = field(
        default=None,
        metadata={
            "name": "Channels_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    channels_original_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Channels_Original_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    channels_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Channels_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    chapter: Optional[str] = field(
        default=None,
        metadata={
            "name": "Chapter",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    chapters_pos_begin: Optional[int] = field(
        default=None,
        metadata={
            "name": "Chapters_Pos_Begin",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    chapters_pos_end: Optional[int] = field(
        default=None,
        metadata={
            "name": "Chapters_Pos_End",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    choregrapher: Optional[str] = field(
        default=None,
        metadata={
            "name": "Choregrapher",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    chroma_subsampling: Optional[str] = field(
        default=None,
        metadata={
            "name": "ChromaSubsampling",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    chroma_subsampling_position: Optional[str] = field(
        default=None,
        metadata={
            "name": "ChromaSubsampling_Position",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    chroma_subsampling_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "ChromaSubsampling_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_cc: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_CC",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_description: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Description",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_extensions: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Extensions",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Family",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_id_compatible: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodecID_Compatible",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_id_description: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodecID_Description",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_id_hint: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodecID_Hint",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_id_info: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodecID_Info",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodecID",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_id_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodecID_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_id_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodecID_Url",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_id_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "CodecID_Version",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_info: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Info",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_profile: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Profile",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_automatic: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_Automatic",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_bvop: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_BVOP",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_cabac: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_CABAC",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_endianness: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_Endianness",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_firm: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_Firm",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_floor: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_Floor",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_gmc: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_GMC",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_gmc_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_GMC_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_itu: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_ITU",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_law: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_Law",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_matrix_data: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_Matrix_Data",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_matrix: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_Matrix",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_packet_bit_stream: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_PacketBitStream",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_qpel: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_QPel",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_ref_frames: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_RefFrames",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_settings_sign: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Settings_Sign",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    codec_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "Codec_Url",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    co_director: Optional[str] = field(
        default=None,
        metadata={
            "name": "CoDirector",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    collection: Optional[str] = field(
        default=None,
        metadata={
            "name": "Collection",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colorimetry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Colorimetry",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    color_space: Optional[str] = field(
        default=None,
        metadata={
            "name": "ColorSpace",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colour_description_present: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colour_description_present_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "colour_description_present_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colour_description_present_original_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "colour_description_present_Original_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colour_description_present_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "colour_description_present_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colour_primaries: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colour_primaries_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "colour_primaries_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colour_primaries_original_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "colour_primaries_Original_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colour_primaries_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "colour_primaries_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colour_range: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colour_range_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "colour_range_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colour_range_original_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "colour_range_Original_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    colour_range_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "colour_range_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    comic: Optional[str] = field(
        default=None,
        metadata={
            "name": "Comic",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    comic_more: Optional[str] = field(
        default=None,
        metadata={
            "name": "Comic_More",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    comic_position_total: Optional[int] = field(
        default=None,
        metadata={
            "name": "Comic_Position_Total",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    comment: Optional[str] = field(
        default=None,
        metadata={
            "name": "Comment",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    commissioned_by: Optional[str] = field(
        default=None,
        metadata={
            "name": "CommissionedBy",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    compilation: Optional[str] = field(
        default=None,
        metadata={
            "name": "Compilation",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    compilation_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Compilation_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    complete_name_last: Optional[str] = field(
        default=None,
        metadata={
            "name": "CompleteName_Last",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    complete_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "CompleteName",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    composer: Optional[str] = field(
        default=None,
        metadata={
            "name": "Composer",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    composer_nationality: Optional[str] = field(
        default=None,
        metadata={
            "name": "Composer_Nationality",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    composer_sort: Optional[str] = field(
        default=None,
        metadata={
            "name": "Composer_Sort",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    compression_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "Compression_Mode",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    compression_mode_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Compression_Mode_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    compression_ratio: Optional[float] = field(
        default=None,
        metadata={
            "name": "Compression_Ratio",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    conductor: Optional[str] = field(
        default=None,
        metadata={
            "name": "Conductor",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    content_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "ContentType",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    co_producer: Optional[str] = field(
        default=None,
        metadata={
            "name": "CoProducer",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    copyright: Optional[str] = field(
        default=None,
        metadata={
            "name": "Copyright",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    copyright_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "Copyright_Url",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    costume_designer: Optional[str] = field(
        default=None,
        metadata={
            "name": "CostumeDesigner",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    count: Optional[int] = field(
        default=None,
        metadata={
            "name": "Count",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    countries: Optional[str] = field(
        default=None,
        metadata={
            "name": "Countries",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    country: Optional[str] = field(
        default=None,
        metadata={
            "name": "Country",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    cover_data: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cover_Data",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    cover_description: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cover_Description",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    cover_mime: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cover_Mime",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    cover: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cover",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    cover_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cover_Type",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    cropped: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cropped",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    data_size: Optional[int] = field(
        default=None,
        metadata={
            "name": "DataSize",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    default: Optional[str] = field(
        default=None,
        metadata={
            "name": "Default",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    default_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Default_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_drop_frame: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_DropFrame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay: Optional[float] = field(
        default=None,
        metadata={
            "name": "Delay",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_original_drop_frame: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_Original_DropFrame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_original: Optional[float] = field(
        default=None,
        metadata={
            "name": "Delay_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_original_settings: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_Original_Settings",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_original_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_Original_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_original_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_Original_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_original_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_Original_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_original_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_Original_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_original_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_Original_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_original_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_Original_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_original_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_Original_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_settings: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_Settings",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_source_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_Source_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    delay_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Delay_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    dimensions: Optional[str] = field(
        default=None,
        metadata={
            "name": "Dimensions",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    director: Optional[str] = field(
        default=None,
        metadata={
            "name": "Director",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    director_of_photography: Optional[str] = field(
        default=None,
        metadata={
            "name": "DirectorOfPhotography",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    disabled: Optional[str] = field(
        default=None,
        metadata={
            "name": "Disabled",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    disabled_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Disabled_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    display_aspect_ratio_clean_aperture: Optional[float] = field(
        default=None,
        metadata={
            "name": "DisplayAspectRatio_CleanAperture",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    display_aspect_ratio_clean_aperture_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "DisplayAspectRatio_CleanAperture_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    display_aspect_ratio: Optional[float] = field(
        default=None,
        metadata={
            "name": "DisplayAspectRatio",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    display_aspect_ratio_original: Optional[float] = field(
        default=None,
        metadata={
            "name": "DisplayAspectRatio_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    display_aspect_ratio_original_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "DisplayAspectRatio_Original_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    display_aspect_ratio_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "DisplayAspectRatio_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    distributed_by: Optional[str] = field(
        default=None,
        metadata={
            "name": "DistributedBy",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    dolby_vision_layers: Optional[str] = field(
        default=None,
        metadata={
            "name": "DolbyVision_Layers",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    dolby_vision_profile: Optional[str] = field(
        default=None,
        metadata={
            "name": "DolbyVision_Profile",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    dolby_vision_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "DolbyVision_Version",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    domain: Optional[str] = field(
        default=None,
        metadata={
            "name": "Domain",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    dots_per_inch: Optional[str] = field(
        default=None,
        metadata={
            "name": "DotsPerInch",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_base: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Base",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_command: Optional[float] = field(
        default=None,
        metadata={
            "name": "Duration_End_Command",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_command_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_End_Command_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_command_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_End_Command_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_command_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_End_Command_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_command_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_End_Command_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_command_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_End_Command_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_command_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_End_Command_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end: Optional[float] = field(
        default=None,
        metadata={
            "name": "Duration_End",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_End_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_End_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_End_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_End_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_End_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_end_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_End_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_first_frame: Optional[float] = field(
        default=None,
        metadata={
            "name": "Duration_FirstFrame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_first_frame_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_FirstFrame_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_first_frame_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_FirstFrame_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_first_frame_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_FirstFrame_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_first_frame_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_FirstFrame_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_first_frame_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_FirstFrame_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_first_frame_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_FirstFrame_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_last_frame: Optional[float] = field(
        default=None,
        metadata={
            "name": "Duration_LastFrame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_last_frame_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_LastFrame_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_last_frame_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_LastFrame_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_last_frame_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_LastFrame_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_last_frame_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_LastFrame_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_last_frame_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_LastFrame_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_last_frame_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_LastFrame_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration: Optional[float] = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start2_end: Optional[float] = field(
        default=None,
        metadata={
            "name": "Duration_Start2End",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start2_end_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start2End_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start2_end_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start2End_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start2_end_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start2End_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start2_end_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start2End_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start2_end_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start2End_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start2_end_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start2End_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_command: Optional[float] = field(
        default=None,
        metadata={
            "name": "Duration_Start_Command",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_command_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start_Command_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_command_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start_Command_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_command_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start_Command_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_command_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start_Command_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_command_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start_Command_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_command_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start_Command_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start: Optional[float] = field(
        default=None,
        metadata={
            "name": "Duration_Start",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_start_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_Start_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    duration_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Duration_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    edited_by: Optional[str] = field(
        default=None,
        metadata={
            "name": "EditedBy",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    element_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "ElementCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_application_company_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Application_CompanyName",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_application: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Application",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_application_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Application_Name",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_application_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Application_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_application_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Application_Url",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_application_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Application_Version",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_by: Optional[str] = field(
        default=None,
        metadata={
            "name": "EncodedBy",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_library_company_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Library_CompanyName",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_library_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Library_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_library: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Library",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_library_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Library_Name",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_library_settings: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Library_Settings",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_library_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Library_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_library_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_Library_Version",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encoded_operating_system: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encoded_OperatingSystem",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encryption_format: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encryption_Format",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encryption_initialization_vector: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encryption_InitializationVector",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encryption_length: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encryption_Length",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encryption_method: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encryption_Method",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encryption: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encryption",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encryption_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encryption_Mode",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    encryption_padding: Optional[str] = field(
        default=None,
        metadata={
            "name": "Encryption_Padding",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    epg_positions_begin: Optional[int] = field(
        default=None,
        metadata={
            "name": "EPG_Positions_Begin",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    epg_positions_end: Optional[int] = field(
        default=None,
        metadata={
            "name": "EPG_Positions_End",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    events_min_duration: Optional[float] = field(
        default=None,
        metadata={
            "name": "Events_MinDuration",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    events_min_duration_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Events_MinDuration_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    events_min_duration_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Events_MinDuration_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    events_min_duration_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Events_MinDuration_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    events_min_duration_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Events_MinDuration_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    events_min_duration_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Events_MinDuration_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    events_min_duration_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Events_MinDuration_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    events_paint_on: Optional[str] = field(
        default=None,
        metadata={
            "name": "Events_PaintOn",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    events_pop_on: Optional[str] = field(
        default=None,
        metadata={
            "name": "Events_PopOn",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    events_roll_up: Optional[str] = field(
        default=None,
        metadata={
            "name": "Events_RollUp",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    events_total: Optional[str] = field(
        default=None,
        metadata={
            "name": "Events_Total",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    executive_producer: Optional[str] = field(
        default=None,
        metadata={
            "name": "ExecutiveProducer",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_created_date_local: Optional[str] = field(
        default=None,
        metadata={
            "name": "File_Created_Date_Local",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_created_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "File_Created_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_extension_last: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileExtension_Last",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_extension: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileExtension",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_modified_date_local: Optional[str] = field(
        default=None,
        metadata={
            "name": "File_Modified_Date_Local",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_modified_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "File_Modified_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_name_extension_last: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileNameExtension_Last",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_name_extension: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileNameExtension",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_name_last: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileName_Last",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileName",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_size: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileSize",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_size_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileSize_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_size_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileSize_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_size_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileSize_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_size_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileSize_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    file_size_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "FileSize_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    first_display_delay_frames: Optional[str] = field(
        default=None,
        metadata={
            "name": "FirstDisplay_Delay_Frames",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    first_display_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "FirstDisplay_Type",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    first_packet_order: Optional[int] = field(
        default=None,
        metadata={
            "name": "FirstPacketOrder",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    folder_name_last: Optional[str] = field(
        default=None,
        metadata={
            "name": "FolderName_Last",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    folder_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "FolderName",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    footer_size: Optional[int] = field(
        default=None,
        metadata={
            "name": "FooterSize",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    forced: Optional[str] = field(
        default=None,
        metadata={
            "name": "Forced",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    forced_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Forced_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_additional_features: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_AdditionalFeatures",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_commercial_if_any: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Commercial_IfAny",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_commercial: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Commercial",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_compression: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Compression",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_extensions: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Extensions",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_info: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Info",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_level: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Level",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_profile: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Profile",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_bvop: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_BVOP",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_bvop_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_BVOP_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_cabac: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_CABAC",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_cabac_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_CABAC_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_emphasis: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Emphasis",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_endianness: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Endianness",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_firm: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Firm",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_floor: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Floor",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_frame_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_FrameMode",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_gmc: Optional[int] = field(
        default=None,
        metadata={
            "name": "Format_Settings_GMC",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_gmc_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_GMC_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_gop: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_GOP",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_itu: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_ITU",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_law: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Law",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_matrix_data: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Matrix_Data",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_matrix: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Matrix",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_matrix_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Matrix_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_mode_extension: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_ModeExtension",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Mode",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_packing: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Packing",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_picture_structure: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_PictureStructure",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_ps: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_PS",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_ps_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_PS_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_pulldown: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Pulldown",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_qpel: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_QPel",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_qpel_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_QPel_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_ref_frames: Optional[int] = field(
        default=None,
        metadata={
            "name": "Format_Settings_RefFrames",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_ref_frames_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_RefFrames_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_sbr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_SBR",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_sbr_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_SBR_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_sign: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Sign",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_slice_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "Format_Settings_SliceCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_slice_count_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_SliceCount_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_settings_wrapping: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Settings_Wrapping",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_tier: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Tier",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Url",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    format_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Format_Version",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "FrameCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_den: Optional[int] = field(
        default=None,
        metadata={
            "name": "FrameRate_Den",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_maximum: Optional[float] = field(
        default=None,
        metadata={
            "name": "FrameRate_Maximum",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_maximum_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "FrameRate_Maximum_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_minimum: Optional[float] = field(
        default=None,
        metadata={
            "name": "FrameRate_Minimum",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_minimum_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "FrameRate_Minimum_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate: Optional[float] = field(
        default=None,
        metadata={
            "name": "FrameRate",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "FrameRate_Mode",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_mode_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "FrameRate_Mode_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_mode_original_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "FrameRate_Mode_Original_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_mode_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "FrameRate_Mode_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_nominal: Optional[float] = field(
        default=None,
        metadata={
            "name": "FrameRate_Nominal",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_nominal_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "FrameRate_Nominal_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_num: Optional[int] = field(
        default=None,
        metadata={
            "name": "FrameRate_Num",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_original_den: Optional[float] = field(
        default=None,
        metadata={
            "name": "FrameRate_Original_Den",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_original: Optional[float] = field(
        default=None,
        metadata={
            "name": "FrameRate_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_original_num: Optional[float] = field(
        default=None,
        metadata={
            "name": "FrameRate_Original_Num",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_original_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "FrameRate_Original_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_real: Optional[float] = field(
        default=None,
        metadata={
            "name": "FrameRate_Real",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_real_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "FrameRate_Real_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    frame_rate_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "FrameRate_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    general_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "GeneralCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    genre: Optional[str] = field(
        default=None,
        metadata={
            "name": "Genre",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    gop_open_closed_first_frame: Optional[str] = field(
        default=None,
        metadata={
            "name": "Gop_OpenClosed_FirstFrame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    gop_open_closed_first_frame_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Gop_OpenClosed_FirstFrame_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    gop_open_closed: Optional[str] = field(
        default=None,
        metadata={
            "name": "Gop_OpenClosed",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    gop_open_closed_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Gop_OpenClosed_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    grouping: Optional[str] = field(
        default=None,
        metadata={
            "name": "Grouping",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    hdr_format_commercial: Optional[str] = field(
        default=None,
        metadata={
            "name": "HDR_Format_Commercial",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    hdr_format_compatibility: Optional[str] = field(
        default=None,
        metadata={
            "name": "HDR_Format_Compatibility",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    hdr_format_level: Optional[str] = field(
        default=None,
        metadata={
            "name": "HDR_Format_Level",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    hdr_format: Optional[str] = field(
        default=None,
        metadata={
            "name": "HDR_Format",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    hdr_format_profile: Optional[str] = field(
        default=None,
        metadata={
            "name": "HDR_Format_Profile",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    hdr_format_settings: Optional[str] = field(
        default=None,
        metadata={
            "name": "HDR_Format_Settings",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    hdr_format_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "HDR_Format_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    hdr_format_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "HDR_Format_Version",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    header_size: Optional[int] = field(
        default=None,
        metadata={
            "name": "HeaderSize",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    height_clean_aperture: Optional[int] = field(
        default=None,
        metadata={
            "name": "Height_CleanAperture",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    height_clean_aperture_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Height_CleanAperture_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    height: Optional[int] = field(
        default=None,
        metadata={
            "name": "Height",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    height_offset: Optional[int] = field(
        default=None,
        metadata={
            "name": "Height_Offset",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    height_offset_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Height_Offset_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    height_original: Optional[int] = field(
        default=None,
        metadata={
            "name": "Height_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    height_original_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Height_Original_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    height_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Height_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    icra: Optional[str] = field(
        default=None,
        metadata={
            "name": "ICRA",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ID",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    id_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "ID_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    image_codec_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Image_Codec_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    image_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "ImageCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    image_format_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Image_Format_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    image_format_with_hint_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Image_Format_WithHint_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    image_language_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Image_Language_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    inform: Optional[str] = field(
        default=None,
        metadata={
            "name": "Inform",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    interlacement: Optional[str] = field(
        default=None,
        metadata={
            "name": "Interlacement",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    interlacement_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Interlacement_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    interleaved: Optional[str] = field(
        default=None,
        metadata={
            "name": "Interleaved",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    interleave_duration: Optional[float] = field(
        default=None,
        metadata={
            "name": "Interleave_Duration",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    interleave_duration_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Interleave_Duration_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    interleave_preload: Optional[float] = field(
        default=None,
        metadata={
            "name": "Interleave_Preload",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    interleave_preload_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Interleave_Preload_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    interleave_video_frames: Optional[float] = field(
        default=None,
        metadata={
            "name": "Interleave_VideoFrames",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    internet_media_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "InternetMediaType",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    isbn: Optional[str] = field(
        default=None,
        metadata={
            "name": "ISBN",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    isrc: Optional[str] = field(
        default=None,
        metadata={
            "name": "ISRC",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    is_streamable: Optional[str] = field(
        default=None,
        metadata={
            "name": "IsStreamable",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    keywords: Optional[str] = field(
        default=None,
        metadata={
            "name": "Keywords",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    label_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "LabelCode",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    label: Optional[str] = field(
        default=None,
        metadata={
            "name": "Label",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    language: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    language_more: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language_More",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    language_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    language_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    language_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    language_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    language_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    law_rating: Optional[str] = field(
        default=None,
        metadata={
            "name": "LawRating",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    law_rating_reason: Optional[str] = field(
        default=None,
        metadata={
            "name": "LawRating_Reason",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    lccn: Optional[str] = field(
        default=None,
        metadata={
            "name": "LCCN",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    lightness: Optional[str] = field(
        default=None,
        metadata={
            "name": "Lightness",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    lines_count: Optional[str] = field(
        default=None,
        metadata={
            "name": "Lines_Count",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    lines_max_count_per_event: Optional[str] = field(
        default=None,
        metadata={
            "name": "Lines_MaxCountPerEvent",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    list_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    list_stream_kind: Optional[str] = field(
        default=None,
        metadata={
            "name": "List_StreamKind",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    list_stream_pos: Optional[str] = field(
        default=None,
        metadata={
            "name": "List_StreamPos",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    list_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "List_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    lyricist: Optional[str] = field(
        default=None,
        metadata={
            "name": "Lyricist",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    lyrics: Optional[str] = field(
        default=None,
        metadata={
            "name": "Lyrics",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mastered_by: Optional[str] = field(
        default=None,
        metadata={
            "name": "MasteredBy",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mastered_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "Mastered_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mastering_display_color_primaries: Optional[str] = field(
        default=None,
        metadata={
            "name": "MasteringDisplay_ColorPrimaries",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mastering_display_color_primaries_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "MasteringDisplay_ColorPrimaries_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mastering_display_color_primaries_original_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "MasteringDisplay_ColorPrimaries_Original_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mastering_display_color_primaries_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "MasteringDisplay_ColorPrimaries_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mastering_display_luminance: Optional[str] = field(
        default=None,
        metadata={
            "name": "MasteringDisplay_Luminance",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mastering_display_luminance_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "MasteringDisplay_Luminance_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mastering_display_luminance_original_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "MasteringDisplay_Luminance_Original_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mastering_display_luminance_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "MasteringDisplay_Luminance_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    matrix_channel_positions: Optional[str] = field(
        default=None,
        metadata={
            "name": "Matrix_ChannelPositions",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    matrix_channel_positions_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Matrix_ChannelPositions_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    matrix_channels: Optional[int] = field(
        default=None,
        metadata={
            "name": "Matrix_Channels",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    matrix_channels_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Matrix_Channels_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    matrix_coefficients: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    matrix_coefficients_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "matrix_coefficients_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    matrix_coefficients_original_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "matrix_coefficients_Original_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    matrix_coefficients_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "matrix_coefficients_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    matrix_format: Optional[str] = field(
        default=None,
        metadata={
            "name": "Matrix_Format",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    max_cll: Optional[str] = field(
        default=None,
        metadata={
            "name": "MaxCLL",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    max_cll_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "MaxCLL_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    max_cll_original_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "MaxCLL_Original_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    max_cll_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "MaxCLL_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    max_fall: Optional[str] = field(
        default=None,
        metadata={
            "name": "MaxFALL",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    max_fall_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "MaxFALL_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    max_fall_original_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "MaxFALL_Original_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    max_fall_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "MaxFALL_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    menu_codec_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Menu_Codec_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    menu_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "MenuCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    menu_format_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Menu_Format_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    menu_format_with_hint_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Menu_Format_WithHint_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    menu_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "MenuID",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    menu_id_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "MenuID_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    menu_language_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Menu_Language_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mood: Optional[str] = field(
        default=None,
        metadata={
            "name": "Mood",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    movie_country: Optional[str] = field(
        default=None,
        metadata={
            "name": "Movie_Country",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    movie: Optional[str] = field(
        default=None,
        metadata={
            "name": "Movie",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    movie_more: Optional[str] = field(
        default=None,
        metadata={
            "name": "Movie_More",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    movie_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "Movie_Url",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    multi_view_base_profile: Optional[str] = field(
        default=None,
        metadata={
            "name": "MultiView_BaseProfile",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    multi_view_count: Optional[str] = field(
        default=None,
        metadata={
            "name": "MultiView_Count",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    multi_view_layout: Optional[str] = field(
        default=None,
        metadata={
            "name": "MultiView_Layout",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    music_by: Optional[str] = field(
        default=None,
        metadata={
            "name": "MusicBy",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    muxing_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "MuxingMode",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    muxing_mode_more_info: Optional[str] = field(
        default=None,
        metadata={
            "name": "MuxingMode_MoreInfo",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    network_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "NetworkName",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_album: Optional[str] = field(
        default=None,
        metadata={
            "name": "Original_Album",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_lyricist: Optional[str] = field(
        default=None,
        metadata={
            "name": "Original_Lyricist",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_movie: Optional[str] = field(
        default=None,
        metadata={
            "name": "Original_Movie",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_network_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Original_NetworkName",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    mediaarea_net_mediainfo_original_network_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginalNetworkName",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_part: Optional[str] = field(
        default=None,
        metadata={
            "name": "Original_Part",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_performer: Optional[str] = field(
        default=None,
        metadata={
            "name": "Original_Performer",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_released_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "Original_Released_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_source_form_cropped: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginalSourceForm_Cropped",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_source_form_distributed_by: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginalSourceForm_DistributedBy",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_source_form: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginalSourceForm",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_source_form_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginalSourceForm_Name",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_source_form_num_colors: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginalSourceForm_NumColors",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_source_form_sharpness: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginalSourceForm_Sharpness",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_source_medium_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginalSourceMedium_ID",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_source_medium_id_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginalSourceMedium_ID_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_source_medium: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginalSourceMedium",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    original_track: Optional[str] = field(
        default=None,
        metadata={
            "name": "Original_Track",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    other_codec_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Other_Codec_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    other_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "OtherCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    other_format_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Other_Format_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    other_format_with_hint_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Other_Format_WithHint_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    other_language_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Other_Language_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    overall_bit_rate_maximum: Optional[float] = field(
        default=None,
        metadata={
            "name": "OverallBitRate_Maximum",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    overall_bit_rate_maximum_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "OverallBitRate_Maximum_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    overall_bit_rate_minimum: Optional[float] = field(
        default=None,
        metadata={
            "name": "OverallBitRate_Minimum",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    overall_bit_rate_minimum_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "OverallBitRate_Minimum_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    overall_bit_rate: Optional[float] = field(
        default=None,
        metadata={
            "name": "OverallBitRate",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    overall_bit_rate_mode: Optional[str] = field(
        default=None,
        metadata={
            "name": "OverallBitRate_Mode",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    overall_bit_rate_mode_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "OverallBitRate_Mode_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    overall_bit_rate_nominal: Optional[float] = field(
        default=None,
        metadata={
            "name": "OverallBitRate_Nominal",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    overall_bit_rate_nominal_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "OverallBitRate_Nominal_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    overall_bit_rate_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "OverallBitRate_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    owner: Optional[str] = field(
        default=None,
        metadata={
            "name": "Owner",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    package_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "PackageName",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    part: Optional[str] = field(
        default=None,
        metadata={
            "name": "Part",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    part_position: Optional[int] = field(
        default=None,
        metadata={
            "name": "Part_Position",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    part_position_total: Optional[int] = field(
        default=None,
        metadata={
            "name": "Part_Position_Total",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    performer: Optional[str] = field(
        default=None,
        metadata={
            "name": "Performer",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    performer_sort: Optional[str] = field(
        default=None,
        metadata={
            "name": "Performer_Sort",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    performer_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "Performer_Url",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    period: Optional[str] = field(
        default=None,
        metadata={
            "name": "Period",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    pixel_aspect_ratio_clean_aperture: Optional[float] = field(
        default=None,
        metadata={
            "name": "PixelAspectRatio_CleanAperture",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    pixel_aspect_ratio_clean_aperture_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "PixelAspectRatio_CleanAperture_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    pixel_aspect_ratio: Optional[float] = field(
        default=None,
        metadata={
            "name": "PixelAspectRatio",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    pixel_aspect_ratio_original: Optional[float] = field(
        default=None,
        metadata={
            "name": "PixelAspectRatio_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    pixel_aspect_ratio_original_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "PixelAspectRatio_Original_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    pixel_aspect_ratio_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "PixelAspectRatio_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    played_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "Played_Count",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    played_first_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "Played_First_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    played_last_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "Played_Last_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    podcast_category: Optional[str] = field(
        default=None,
        metadata={
            "name": "PodcastCategory",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    producer_copyright: Optional[str] = field(
        default=None,
        metadata={
            "name": "Producer_Copyright",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    producer: Optional[str] = field(
        default=None,
        metadata={
            "name": "Producer",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    production_designer: Optional[str] = field(
        default=None,
        metadata={
            "name": "ProductionDesigner",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    production_studio: Optional[str] = field(
        default=None,
        metadata={
            "name": "ProductionStudio",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    publisher: Optional[str] = field(
        default=None,
        metadata={
            "name": "Publisher",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    publisher_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "Publisher_URL",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    rating: Optional[str] = field(
        default=None,
        metadata={
            "name": "Rating",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    recorded_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "Recorded_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    recorded_location: Optional[str] = field(
        default=None,
        metadata={
            "name": "Recorded_Location",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    reel: Optional[str] = field(
        default=None,
        metadata={
            "name": "Reel",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    reel_position: Optional[int] = field(
        default=None,
        metadata={
            "name": "Reel_Position",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    reel_position_total: Optional[int] = field(
        default=None,
        metadata={
            "name": "Reel_Position_Total",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    released_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "Released_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    remixed_by: Optional[str] = field(
        default=None,
        metadata={
            "name": "RemixedBy",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    replay_gain_gain: Optional[str] = field(
        default=None,
        metadata={
            "name": "ReplayGain_Gain",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    replay_gain_gain_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "ReplayGain_Gain_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    replay_gain_peak: Optional[str] = field(
        default=None,
        metadata={
            "name": "ReplayGain_Peak",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    resolution: Optional[int] = field(
        default=None,
        metadata={
            "name": "Resolution",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    resolution_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Resolution_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    rotation: Optional[str] = field(
        default=None,
        metadata={
            "name": "Rotation",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    rotation_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Rotation_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    sampled_height: Optional[int] = field(
        default=None,
        metadata={
            "name": "Sampled_Height",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    sampled_width: Optional[int] = field(
        default=None,
        metadata={
            "name": "Sampled_Width",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    samples_per_frame: Optional[float] = field(
        default=None,
        metadata={
            "name": "SamplesPerFrame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    sampling_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "SamplingCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    sampling_rate: Optional[float] = field(
        default=None,
        metadata={
            "name": "SamplingRate",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    sampling_rate_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "SamplingRate_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_order: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanOrder",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_order_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanOrder_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_order_original_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanOrder_Original_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_order_stored_displayed_inverted: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanOrder_StoredDisplayedInverted",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_order_stored: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanOrder_Stored",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_order_stored_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanOrder_Stored_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_order_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanOrder_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanType",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_type_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanType_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_type_original_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanType_Original_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_type_store_method_fields_per_block: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanType_StoreMethod_FieldsPerBlock",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_type_store_method: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanType_StoreMethod",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_type_store_method_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanType_StoreMethod_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    scan_type_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScanType_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    screenplay_by: Optional[str] = field(
        default=None,
        metadata={
            "name": "ScreenplayBy",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    season: Optional[str] = field(
        default=None,
        metadata={
            "name": "Season",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    season_position: Optional[int] = field(
        default=None,
        metadata={
            "name": "Season_Position",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    season_position_total: Optional[int] = field(
        default=None,
        metadata={
            "name": "Season_Position_Total",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    service_channel: Optional[str] = field(
        default=None,
        metadata={
            "name": "ServiceChannel",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    service_kind: Optional[str] = field(
        default=None,
        metadata={
            "name": "ServiceKind",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    service_kind_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "ServiceKind_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    service_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "ServiceName",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    service_provider: Optional[str] = field(
        default=None,
        metadata={
            "name": "ServiceProvider",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    service_provider_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "ServiceProvider_Url",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    service_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "ServiceType",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    service_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "Service_Url",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    sound_engineer: Optional[str] = field(
        default=None,
        metadata={
            "name": "SoundEngineer",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_first_frame: Optional[float] = field(
        default=None,
        metadata={
            "name": "Source_Duration_FirstFrame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_first_frame_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_FirstFrame_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_first_frame_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_FirstFrame_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_first_frame_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_FirstFrame_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_first_frame_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_FirstFrame_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_first_frame_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_FirstFrame_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_first_frame_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_FirstFrame_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_last_frame: Optional[float] = field(
        default=None,
        metadata={
            "name": "Source_Duration_LastFrame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_last_frame_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_LastFrame_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_last_frame_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_LastFrame_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_last_frame_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_LastFrame_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_last_frame_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_LastFrame_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_last_frame_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_LastFrame_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_last_frame_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_LastFrame_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration: Optional[float] = field(
        default=None,
        metadata={
            "name": "Source_Duration",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_duration_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_Duration_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_frame_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "Source_FrameCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_sampling_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "Source_SamplingCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_encoded: Optional[int] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_Encoded",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_encoded_proportion: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_Encoded_Proportion",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_encoded_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_Encoded_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_encoded_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_Encoded_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_encoded_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_Encoded_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_encoded_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_Encoded_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_encoded_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_Encoded_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_encoded_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_Encoded_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size: Optional[int] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_proportion: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_Proportion",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    source_stream_size_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Source_StreamSize_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    standard: Optional[str] = field(
        default=None,
        metadata={
            "name": "Standard",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    status: Optional[int] = field(
        default=None,
        metadata={
            "name": "Status",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stored_height: Optional[int] = field(
        default=None,
        metadata={
            "name": "Stored_Height",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stored_width: Optional[int] = field(
        default=None,
        metadata={
            "name": "Stored_Width",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "StreamCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_kind_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "StreamKindID",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_kind: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamKind",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_kind_pos: Optional[int] = field(
        default=None,
        metadata={
            "name": "StreamKindPos",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_kind_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamKind_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_order: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamOrder",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_demuxed: Optional[int] = field(
        default=None,
        metadata={
            "name": "StreamSize_Demuxed",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_demuxed_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Demuxed_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_demuxed_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Demuxed_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_demuxed_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Demuxed_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_demuxed_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Demuxed_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_demuxed_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Demuxed_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_demuxed_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Demuxed_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_encoded: Optional[int] = field(
        default=None,
        metadata={
            "name": "StreamSize_Encoded",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_encoded_proportion: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Encoded_Proportion",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_encoded_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Encoded_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_encoded_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Encoded_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_encoded_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Encoded_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_encoded_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Encoded_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_encoded_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Encoded_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_encoded_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Encoded_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size: Optional[int] = field(
        default=None,
        metadata={
            "name": "StreamSize",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_proportion: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_Proportion",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    stream_size_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "StreamSize_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    subject: Optional[str] = field(
        default=None,
        metadata={
            "name": "Subject",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    sub_track: Optional[str] = field(
        default=None,
        metadata={
            "name": "SubTrack",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    summary: Optional[str] = field(
        default=None,
        metadata={
            "name": "Summary",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    synopsis: Optional[str] = field(
        default=None,
        metadata={
            "name": "Synopsis",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    tagged_application: Optional[str] = field(
        default=None,
        metadata={
            "name": "Tagged_Application",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    tagged_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "Tagged_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    terms_of_use: Optional[str] = field(
        default=None,
        metadata={
            "name": "TermsOfUse",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    text_codec_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Text_Codec_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    text_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "TextCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    text_format_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Text_Format_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    text_format_with_hint_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Text_Format_WithHint_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    text_language_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Text_Language_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    thanks_to: Optional[str] = field(
        default=None,
        metadata={
            "name": "ThanksTo",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_code_drop_frame: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeCode_DropFrame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_code_first_frame: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeCode_FirstFrame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_code_last_frame: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeCode_LastFrame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_code_max_frame_number: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeCode_MaxFrameNumber",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_code_max_frame_number_theory: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeCode_MaxFrameNumber_Theory",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_code_settings: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeCode_Settings",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_code_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeCode_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_code_striped: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeCode_Striped",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_code_striped_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeCode_Striped_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_code_stripped: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeCode_Stripped",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_code_stripped_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeCode_Stripped_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_stamp_first_frame: Optional[float] = field(
        default=None,
        metadata={
            "name": "TimeStamp_FirstFrame",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_stamp_first_frame_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeStamp_FirstFrame_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_stamp_first_frame_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeStamp_FirstFrame_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_stamp_first_frame_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeStamp_FirstFrame_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_stamp_first_frame_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeStamp_FirstFrame_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_stamp_first_frame_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeStamp_FirstFrame_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_stamp_first_frame_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeStamp_FirstFrame_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_zone: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeZone",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    time_zones: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeZones",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    title: Optional[str] = field(
        default=None,
        metadata={
            "name": "Title",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    title_more: Optional[str] = field(
        default=None,
        metadata={
            "name": "Title_More",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    title_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "Title_Url",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    track: Optional[str] = field(
        default=None,
        metadata={
            "name": "Track",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    track_more: Optional[str] = field(
        default=None,
        metadata={
            "name": "Track_More",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    track_position: Optional[int] = field(
        default=None,
        metadata={
            "name": "Track_Position",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    track_position_total: Optional[int] = field(
        default=None,
        metadata={
            "name": "Track_Position_Total",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    track_sort: Optional[str] = field(
        default=None,
        metadata={
            "name": "Track_Sort",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    track_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "Track_Url",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    transfer_characteristics: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    transfer_characteristics_original: Optional[str] = field(
        default=None,
        metadata={
            "name": "transfer_characteristics_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    transfer_characteristics_original_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "transfer_characteristics_Original_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    transfer_characteristics_source: Optional[str] = field(
        default=None,
        metadata={
            "name": "transfer_characteristics_Source",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    type_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    umid: Optional[str] = field(
        default=None,
        metadata={
            "name": "UMID",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    unique_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "UniqueID",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    unique_id_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "UniqueID_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    universal_ad_id_registry: Optional[str] = field(
        default=None,
        metadata={
            "name": "UniversalAdID_Registry",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    universal_ad_id_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "UniversalAdID_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    universal_ad_id_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "UniversalAdID_Value",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video0_delay: Optional[int] = field(
        default=None,
        metadata={
            "name": "Video0_Delay",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video0_delay_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video0_Delay_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video0_delay_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video0_Delay_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video0_delay_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video0_Delay_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video0_delay_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video0_Delay_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video0_delay_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video0_Delay_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video0_delay_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video0_Delay_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video_codec_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video_Codec_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video_count: Optional[int] = field(
        default=None,
        metadata={
            "name": "VideoCount",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video_delay: Optional[float] = field(
        default=None,
        metadata={
            "name": "Video_Delay",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video_delay_string1: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video_Delay_String1",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video_delay_string2: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video_Delay_String2",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video_delay_string3: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video_Delay_String3",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video_delay_string4: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video_Delay_String4",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video_delay_string5: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video_Delay_String5",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video_delay_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video_Delay_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video_format_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video_Format_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video_format_with_hint_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video_Format_WithHint_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    video_language_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "Video_Language_List",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    width_clean_aperture: Optional[int] = field(
        default=None,
        metadata={
            "name": "Width_CleanAperture",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    width_clean_aperture_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Width_CleanAperture_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    width: Optional[int] = field(
        default=None,
        metadata={
            "name": "Width",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    width_offset: Optional[int] = field(
        default=None,
        metadata={
            "name": "Width_Offset",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    width_offset_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Width_Offset_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    width_original: Optional[int] = field(
        default=None,
        metadata={
            "name": "Width_Original",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    width_original_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Width_Original_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    width_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "Width_String",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    written_by: Optional[str] = field(
        default=None,
        metadata={
            "name": "WrittenBy",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    written_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "Written_Date",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    written_location: Optional[str] = field(
        default=None,
        metadata={
            "name": "Written_Location",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    track_type: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    typeorder: str = field(
        default="1",
        metadata={
            "type": "Attribute",
        },
    )


class Media(BaseModel):
    class Meta:
        name = "media"

    track: list[Track] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    ref: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class MediaInfo(BaseModel):
    class Meta:
        name = "MediaInfo"
        namespace = __NAMESPACE__

    creating_application: Optional[Creation] = field(
        default=None,
        metadata={
            "name": "creatingApplication",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    creating_library: Optional[Creation] = field(
        default=None,
        metadata={
            "name": "creatingLibrary",
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    media: list[Media] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    track: list[Track] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": __NAMESPACE__,
        },
    )
    version: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )

    @cached_property
    def tracks(self) -> list[Track]:
        return [*itertools.chain.from_iterable(media.track for media in self.media)]

    def _tracks(self, track_type: str) -> list[Track]:
        return [track for track in self.tracks if track.track_type == track_type]

    @property
    def general_tracks(self) -> list[Track]:
        return self._tracks("General")

    @property
    def video_tracks(self) -> list[Track]:
        return self._tracks("Video")

    @property
    def audio_tracks(self) -> list[Track]:
        return self._tracks("Audio")

    @property
    def text_tracks(self) -> list[Track]:
        return self._tracks("Text")

    @property
    def other_tracks(self) -> list[Track]:
        return self._tracks("Other")

    @property
    def image_tracks(self) -> list[Track]:
        return self._tracks("Image")

    @property
    def menu_tracks(self) -> list[Track]:
        return self._tracks("Menu")
