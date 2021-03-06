import argparse, struct

def die(msg="killed by user"):
    print(msg)
    from sys import exit
    exit()

class Chunk:
    def __init__(self,length, pos, type, data, crc):
        self.pos = pos #where we found it?
        self.length = length #how long it is
        self.type = type #what the type text is

        #data and CRC byte arrays
        self.data = data
        self.crc = crc
        self.critical = False   #false = ancillary
        self.public = True      # false = private
        self.reserved = True    #this must be uppercase in this version of PNG
        self.unsafe = False     # unsafe to copy
        self.attributes()

    def __str__(self):
        return self.type

    def attributes(self):
        # note that this should be checking the 5th bit of each byte, because:
        # 1) checking for lowercase is inefficient blah blah
        # 2) lowercase check might be incorrect if a locale-specific case definition is used
        self.critical   = self.type[0].isupper()
        self.public     = self.type[1].isupper()
        self.reserved   = self.type[2].isupper()
        self.unsafe     = self.type[3].isupper()

    def crc_check(self):
        print("to be implemented")

class Png:

    def __init__(self, img_name):
        self.filename = img_name

        self.chunks = self.read_file(self.filename)

        dimensions = self.read_header()
        if dimensions is not None:
            (self.width, self.height) = dimensions

    def read_file(self, img_name):
        chunks = []
        cursor = 8 # fuck the header
        with open(img_name) as img_file:
            while 1:

            #ew this is gross i hate this can we migrate to py3 and turn this into an iterator pls
            # is py 3 necessary to do this properly? idk
                chunk = self.read_chunk(img_file, cursor)
                if chunk is None:
                    break
                chunks.append(chunk)
                cursor += 8 + chunk.length + 4 # CRC
        return chunks


    def read_chunk(self, imgf, cursor):
        imgf.seek(cursor)
        len_bytes = imgf.read(4)
        if len(len_bytes) < 4: #EOF
            return None
        clen = struct.unpack("!I",len_bytes)[0]

        type_bytes = imgf.read(4)
        data_bytes = imgf.read(clen)
        crc_bytes = imgf.read(4)

        if len(crc_bytes)+len(type_bytes) < 8 or len(data_bytes) < clen: #something fucked up
            print("Error: we shouldn't be in this part of the file")
            return None

        chunk_type = ''.join(type_bytes)

        chunk = Chunk(clen, cursor, chunk_type, data_bytes, crc_bytes)

        return chunk

    def list_chunks(self):
        return [str(c) for c in self.chunks]

    def read_header(self):
        IHDR = self.chunks[0]
        try:
            assert IHDR.type=="IHDR"
        except AssertionError:
            print("The first chunk wasn't the header!")
            return
        width = struct.unpack("!I", self.chunks[0].data[0x0:0x4])[0]
        height = struct.unpack("!I", self.chunks[0].data[0x4:0x8])[0]

        return (width, height)

def main():
    parser = argparse.ArgumentParser(description="Let's fuck up some PNGs!")
    parser.add_argument('png')
    args = parser.parse_args()
    png = Png(args.png)
    print(png.list_chunks())

if __name__ == '__main__':
    main()


