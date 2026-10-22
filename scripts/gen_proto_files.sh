cd libresvip/res/protos
uv run -- buf generate
# Shed the .proto excerpts protoc-gen-py embeds in each docstring: the schemas
# already live in libresvip/res/protos/, and the copies only bloat the stubs.
uv run -- python ../../../scripts/strip_proto_docstrings.py svip3_pb.py libresvip_pb.py
# Generated stubs belong next to the modules that import them.
cp svip3_pb.py ../../plugins/svip3/svip3_pb.py
cp libresvip_pb.py ../../cli/rpc/libresvip_pb.py
rm svip3_pb.py libresvip_pb.py
