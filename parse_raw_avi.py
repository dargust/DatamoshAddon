#############################################################################
# Datamosh addon for blender                                                #
# Copyright (C) 2025 Dan Argust                                             #
#                                                                           #
#    This program is free software: you can redistribute it and/or modify   #
#    it under the terms of the GNU General Public License as published by   #
#    the Free Software Foundation, either version 3 of the License, or      #
#    (at your option) any later version.                                    #
#                                                                           #
#    This program is distributed in the hope that it will be useful,        #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#    GNU General Public License for more details.                           #
#                                                                           #
#    You should have received a copy of the GNU General Public License      #
#    along with this program.  If not, see <https://www.gnu.org/licenses/>. #
#############################################################################

from enum import Enum
import struct
import subprocess
debug_global = 0

# Convert to AVI (Xvid is best for datamoshing)
def convert_to_avi(input_file, output_file, compression=3):
    cmd = f'ffmpeg -i "{input_file}" -y -c:v libxvid -q:v {compression} -an "{output_file}"'
    subprocess.run(cmd, shell=True)

class FrameType(Enum):
    UncompressedVideoFrame = b'db'
    CompressedVideoFrame = b'dc'
    PaletteChange = b'pc'
    AudioData = b'wb'

    # I-frames
    I = b'\xb0'
    P = b'\xb6'

def collect_riff_data(avi_data):
    riff_start = avi_data.find(b"RIFF")
    riff_size = int.from_bytes(avi_data[riff_start + 4:riff_start + 8], "little")
    riff_data = avi_data[riff_start:riff_start + riff_size + 8]
    fileSize = int.from_bytes(avi_data[4:8], "little")
    fileType = avi_data[8:12].decode("utf-8")
    return {"start": riff_start, "size": riff_size, "data": riff_data, "fileSize": fileSize, "fileType": fileType}

def collect_avih_data(avi_data, hdrl_start):
    avih_start = avi_data.find(b"avih", hdrl_start)
    avih_size = int.from_bytes(avi_data[avih_start + 4:avih_start + 8], "little")
    avih_data = avi_data[avih_start:avih_start + avih_size + 8]
    microsec_per_frame = int.from_bytes(avi_data[avih_start + 8:avih_start + 12], "little")
    max_bytes_per_sec = int.from_bytes(avi_data[avih_start + 12:avih_start + 16], "little")
    padding_granularity = int.from_bytes(avi_data[avih_start + 16:avih_start + 20], "little")
    flags = int.from_bytes(avi_data[avih_start + 20:avih_start + 24], "little")
    total_frames = int.from_bytes(avi_data[avih_start + 24:avih_start + 28], "little")
    initial_frames = int.from_bytes(avi_data[avih_start + 28:avih_start + 32], "little")
    streams = int.from_bytes(avi_data[avih_start + 32:avih_start + 36], "little")
    suggested_buffer_size = int.from_bytes(avi_data[avih_start + 36:avih_start + 40], "little")
    width = int.from_bytes(avi_data[avih_start + 40:avih_start + 44], "little")
    height = int.from_bytes(avi_data[avih_start + 44:avih_start + 48], "little")
    reserved = int.from_bytes(avi_data[avih_start + 48:avih_start + 52], "little")
    return {"start": avih_start, "size": avih_size, "data": avih_data, "microsec_per_frame": microsec_per_frame, "max_bytes_per_sec": max_bytes_per_sec, "padding_granularity": padding_granularity, "flags": flags, "total_frames": total_frames, "initial_frames": initial_frames, "streams": streams, "suggested_buffer_size": suggested_buffer_size, "width": width, "height": height, "reserved": reserved}

def collect_strl_data(avi_data, hdrl_start):
    strl_start = avi_data.find(b"strl", hdrl_start)
    strl_size = int.from_bytes(avi_data[strl_start + 4:strl_start + 8], "little")
    strl_data = avi_data[strl_start:strl_start + strl_size + 8]
    return {"start": strl_start, "size": strl_size, "data": strl_data}

def collect_strh_data(avi_data, hdrl_start):
    strh_start = avi_data.find(b"strh", hdrl_start)
    strh_size = int.from_bytes(avi_data[strh_start + 4:strh_start + 8], "little")
    strh_data = avi_data[strh_start:strh_start + strh_size + 8]
    return {"start": strh_start, "size": strh_size, "data": strh_data}

def collect_strf_data(avi_data, hdrl_start):
    strf_start = avi_data.find(b"strf", hdrl_start)
    strf_size = int.from_bytes(avi_data[strf_start + 4:strf_start + 8], "little")
    strf_data = avi_data[strf_start:strf_start + strf_size + 8]
    return {"start": strf_start, "size": strf_size, "data": strf_data}

def collect_hdrl_data(avi_data):
    hdrl_start = avi_data.find(b"hdrl")
    hdrl_size = int.from_bytes(avi_data[hdrl_start + 4:hdrl_start + 8], "little")
    hdrl_data = avi_data[hdrl_start:hdrl_start + hdrl_size + 8]
    avih_data = collect_avih_data(avi_data, hdrl_start)
    strl_data = collect_strl_data(avi_data, hdrl_start)
    strh_data = collect_strh_data(avi_data, hdrl_start)
    strf_data = collect_strf_data(avi_data, hdrl_start)
    return {"start": hdrl_start, "size": hdrl_size, "data": hdrl_data, "avih": avih_data, "strl": strl_data, "strh": strh_data, "strf": strf_data}

def collect_frame_data(avi_data, movi_start, total_frames):
    #global debug_global
    frame_data = []
    frame_types = []
    for i in range(total_frames):
        frame_start = avi_data.find(b"00dc", movi_start)
        frame_size = int.from_bytes(avi_data[frame_start + 4:frame_start + 8], "little")
        frame_data.append({"start": frame_start, "size": frame_size, "data": avi_data[frame_start:frame_start + frame_size + 8]})
        # Work out if the frame is an I frame or a B/P frame
        frame_type = avi_data[frame_start + 11:frame_start + 12]
        frame_types.append(frame_type)
        #if debug_global == 3:
        #    print(f"frame type: {frame_type}")
        #debug_global += 1
        movi_start = frame_start + frame_size
        
    return {"frame_data": frame_data, "frame_types": frame_types}
    
def collect_movi_data(avi_data, total_frames):
    movi_start = avi_data.find(b"movi")
    movi_size = int.from_bytes(avi_data[movi_start + 4:movi_start + 8], "little")
    movi_data = avi_data[movi_start:movi_start + movi_size + 8]
    frame_data = collect_frame_data(avi_data, movi_start, total_frames)
    return {"start": movi_start, "size": movi_size, "data": movi_data, "frame_data": frame_data}

def collect_idx1_data(avi_data):
    idx1_start = avi_data.find(b"idx1")
    idx1_size = int.from_bytes(avi_data[idx1_start + 4:idx1_start + 8], "little")
    idx1_data = avi_data[idx1_start:idx1_start + idx1_size + 8]
    idx1_entries = []
    entry_size = 16  # Each idx1 entry is 16 bytes long
    idx1_end = 0
    for i in range(0, idx1_size, entry_size):
        entry_start = idx1_start + 8 + i
        chunk_id = avi_data[entry_start:entry_start + 4]
        flags = int.from_bytes(avi_data[entry_start + 4:entry_start + 8], "little")
        offset = int.from_bytes(avi_data[entry_start + 8:entry_start + 12], "little")
        size = int.from_bytes(avi_data[entry_start + 12:entry_start + 16], "little")
        idx1_entries.append({"chunk_id": chunk_id, "flags": flags, "offset": offset, "size": size})
        idx1_end = entry_start + entry_size
    return {"start": idx1_start, "size": idx1_size, "data": idx1_data, "entries": idx1_entries, "end": idx1_end}

def extract_avi_data(input_file):
    with open(input_file, "rb") as f_in:
        avi_data = f_in.read()

        riff_data = collect_riff_data(avi_data)
        print(f"riff start: {riff_data['start']}, size: {riff_data['size']}")
        print(f"    file size: {riff_data['fileSize']}")
        print(f"    file type: {riff_data['fileType']}")

        hdrl_data = collect_hdrl_data(avi_data)
        total_frames = hdrl_data["avih"]["total_frames"]
        print(f"hdrl start: {hdrl_data['start']}, size: {hdrl_data['size']}")
        print(f"    total frames: {total_frames}")
        print(f"    video dimensions: {hdrl_data['avih']['width']}x{hdrl_data['avih']['height']}")

        movi_data = collect_movi_data(avi_data, total_frames)
        print(f"movi start: {movi_data['start']}, size: {movi_data['size']}")
        print("    number of I frames: {}".format(movi_data['frame_data']['frame_types'].count(b'\xb0')))
        print("    number of P frames: {}".format(movi_data['frame_data']['frame_types'].count(b'\xb6')))
        i = 0
        for frame in movi_data['frame_data']['frame_data']:
            if i < 3:
                print(f"        frame start: {frame['start']}, size: {frame['size']}")
            i += 1
        if i > 3:
            print("        ...")

        idx1_data = collect_idx1_data(avi_data)
        print(f"idx1 start: {idx1_data['start']}, size: {idx1_data['size']}")
        i = 0
        for entry in idx1_data['entries']:
            if i < 3:
                print(f"        chunk id: {entry['chunk_id']}, offset: {entry['offset']}, size: {entry['size']}")
            i += 1
        if i > 3:
            print("        ...")

    return {"riff": riff_data, "hdrl": hdrl_data, "movi": movi_data, "idx1": idx1_data}

def create_datamoshed_avi(avi_data, input_filename, output_filename, start_at=2, end_at=1000, duplicated_p_frames=1, transition_frames=None):
    print("#### Datamoshing AVI file...")
    print("removing I-frames and replacing them with duplicated P-frames...")
    print(f"start points: {start_at}, end points: {end_at}, transitions: {transition_frames}")
    new_file_data = bytearray()
    print_writes = False
    with open(input_filename, "rb") as f_in:
        raw_file_data = f_in.read()
        riff_start = avi_data["riff"]["start"]
        hdrl_start = avi_data["hdrl"]["start"]
        movi_start = avi_data["movi"]["start"]
        idx1_start = avi_data["idx1"]["start"]
        # Don't modify the RIFF chunk
        new_file_data.extend(raw_file_data[riff_start:hdrl_start])
        if print_writes: print(f"writing riff from {riff_start} to {hdrl_start}")
        # Don't modify the HDLR/AVIH chunk
        new_file_data.extend(raw_file_data[hdrl_start:movi_start])
        if print_writes: print(f"writing hdrl from {hdrl_start} to {movi_start}")
        # Modify the MOVI chunk by removing I-frames and duplicating P-frames
        modified_frame_starts = []
        modified_frame_ends = []
        first_frame_start = avi_data["movi"]["frame_data"]["frame_data"][0]["start"]
        new_file_data.extend(raw_file_data[movi_start:first_frame_start])
        if print_writes: print(f"writing movi from {movi_start} to {first_frame_start}")
        frame_count = len(avi_data["movi"]["frame_data"]["frame_data"])
        last_frame_binary = None
        skipped_frames = 0
        removing = False
        for i in range(frame_count):
            frame = avi_data["movi"]["frame_data"]["frame_data"][i]
            frame_start = frame["start"]
            next_frame_start = avi_data["movi"]["frame_data"]["frame_data"][i + 1]["start"] if i + 1 < frame_count else idx1_start
            frame_type = avi_data["movi"]["frame_data"]["frame_types"][i]
            raw_binary = raw_file_data[frame_start:next_frame_start]
            if not i in transition_frames:
                if any([(start_at[q] <= i <= end_at[q]) for q in range(len(start_at))]):
                    if not removing:
                        print(f"removing I-frames from frame {i}...")
                    removing = True
                    if frame_type == FrameType.I.value:
                        print(f"    swapping I-frame at {i}")
                        raw_binary = last_frame_binary
                        new_file_data.extend(last_frame_binary)
                        for j in range(duplicated_p_frames):
                            new_file_data.extend(last_frame_binary)
                            skipped_frames -= 1
                    else:
                        pass
                        new_file_data.extend(raw_binary)
                else:
                    if removing:
                        print(f"resuming I-frames at frame {i}")
                    removing = False
                    new_file_data.extend(raw_binary)
            else:
                print(f"    explicitly skipping frame {i} for transition...")
                skipped_frames += 1
            if print_writes: print(f"writing fram from {frame_start} to {next_frame_start}, type: {frame_type}")
            if frame_type == FrameType.P.value:
                last_frame_binary = raw_binary
        new_file_data.extend(raw_file_data[next_frame_start:idx1_start])
        if print_writes: print(f"writing mend from {next_frame_start} to {idx1_start}")

        # Modify the IDX1 chunk by updating the index entries
        for entry in avi_data["idx1"]["entries"]:
            chunk_id = entry["chunk_id"]
            flags = entry["flags"]
            offset = entry["offset"]
            size = entry["size"]
            new_file_data.extend(chunk_id)
            new_file_data.extend(struct.pack('<I', flags))
            new_file_data.extend(struct.pack('<I', offset))
            new_file_data.extend(struct.pack('<I', size))
        new_file_data.extend(raw_file_data[avi_data["idx1"]["end"]:])

        if print_writes: print(f"writing idx1 from {idx1_start} to end")
    
    new_frame_count = len(avi_data["movi"]["frame_data"]["frame_data"]) - skipped_frames
    print(f"Old frame count: {len(avi_data['movi']['frame_data']['frame_data'])}, new frame count: {new_frame_count}")
    struct.pack_into('<I', new_file_data, 16, new_frame_count)
    

    with open(output_filename, "wb") as f_out:
        f_out.write(new_file_data)
    print(f"#### Datamosh complete. Saved to: {output_filename}")

if __name__ == "__main__":
    # Example usage
    convert_to_avi("test.mp4", "temp.avi", compression=15)
    input_file = "temp.avi"
    output_file = "output_glitched.avi"
    avi_data = extract_avi_data(input_file)
    create_datamoshed_avi(avi_data, input_file, output_file, start_at=[143,275,545,673], end_at=[243,325,665,723], duplicated_p_frames=0, transition_frames=[153,285,555,683])