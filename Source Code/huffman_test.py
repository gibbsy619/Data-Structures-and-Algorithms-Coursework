from bitstring import BitArray


# function to get all the characters in the text sting so that nodes can be later created
def get_characters(text):
    characters = []
    for character in text:
        if character not in characters:
            characters.append(character)
    return characters


# Iterates through all the text and counts how many times each character occurs
def get_frequencies(text):
    dictionary_of_frequencies = {}
    for i in text:
        dictionary_of_frequencies[i] = dictionary_of_frequencies.get(i, 0) + 1
    frequency = list(dictionary_of_frequencies.values())
    return frequency


# replaces each character in the text string to its huffman code created earlier
def encoded_huffman_data(inputted_string, codes):
    encoded_string = ""
    for character in inputted_string:
        encoded_string += codes[character]
    return encoded_string


# adding padding to the back of the string so that it can be sent to a binary file
def pad_encoded_text(encoded_text):
    extra_padding = 8 - len(encoded_text) % 8
    for i in range(extra_padding):
        encoded_text += "0"
    # converts the number of extra zeros added to back of string before to an 8 bit binary number
    # then adds this to front of string to tell the decoder later how many zeros to remove from back of string
    padded_info = "{0:08b}".format(extra_padding)
    encoded_text = padded_info + encoded_text
    return encoded_text


# removes the padding previously included to allow the encoded string to convert to a binary file
def remove_padding(padded_encoded_text):
    padded_info = padded_encoded_text[:8]  # gets the information about padding from beginning of string
    extra_padding = int(padded_info, 2)  # converts this binary number to an integer

    padded_encoded_text = padded_encoded_text[8:]
    encoded_text = padded_encoded_text[:-1 * extra_padding]  # removes the padding from back of string

    return encoded_text


class HuffmanCoding:
    def __init__(self, path):
        self.path = path
        self.nodes = []
        self.codes = {}

    # class to create each Huffman Tree Node
    class Node:
        def __init__(self, frequency, character, left=None, right=None):
            self.frequency = frequency  # frequency of each character
            self.character = character  # symbol of character
            self.left = left  # node left of current node
            self.right = right  # node right of current node
            self.direction = ''  # tree direction (0/1)

    # traverses the Huffman Tree to create a character code for each character
    def make_codes(self, node, code='', codes={}):
        character_code = code + str(node.direction)  # cumulative code for how far the tree has been traversed
        # checks if the current node is a root into another node
        if node.left:
            self.make_codes(node.left, character_code)
        if node.right:
            self.make_codes(node.right, character_code)
        # if node reaches a node with a character inside, display character_code
        if not node.left and not node.right:
            codes[node.character] = character_code
        return codes

    # creates nodes for each character and their respective frequencies
    def get_huffman_tree_nodes(self, frequency, characters, nodes=[]):
        for x in range(len(characters)):
            nodes.append(self.Node(frequency[x], characters[x]))
        return nodes

    # sorts each characters node by frequency to merge them together and create the root node
    def merge_nodes(self, nodes):
        while len(nodes) > 1:
            nodes = sorted(nodes, key=lambda x: x.frequency)  # function to sort every node by its frequency

            # get two smallest nodes
            left = nodes[0]
            right = nodes[1]

            # create directional code to allow for the creation of character codes later
            left.direction = 0
            right.direction = 1

            # merges two smallest nodes in the array to create a parent node that will go on to finally become the
            # root node
            parent_node = self.Node(left.frequency + right.frequency, left.character + right.character, left, right)

            nodes.remove(left)
            nodes.remove(right)
            nodes.append(parent_node)  # only parent node stays in tree
        return nodes

    # goes through all the bits in the file until a concatenated code matches a code in the codes dictionary
    def decoded_huffman_data(self, encoded_string):
        decoded_file = ""
        character_bits = ""
        for bit in encoded_string:
            character_bits += bit
            for character, code in self.codes.items():
                if character_bits == code:
                    found_character = character
                    decoded_file += found_character
                    character_bits = ""
        return decoded_file

    # combines all compressing functions above to turn a text file into a compression binary file
    def compress(self, path, binary_file):
        final_path = binary_file
        # encoding needed to be specified so that texts in all languages can be compressed and their characters
        # recognised
        with open(path, 'r+', encoding="utf-8") as file, open(final_path, 'wb') as output:
            text = file.read()
            text = text.rstrip()

            frequency = get_frequencies(text)
            characters = get_characters(text)
            nodes = self.get_huffman_tree_nodes(frequency, characters)
            merged_nodes = self.merge_nodes(nodes)
            self.codes = self.make_codes(merged_nodes[0])

            encoded_text = encoded_huffman_data(text, self.codes)

            padded_encoded_text = pad_encoded_text(encoded_text)
            # BitArray function to create an array of bits to be sent to a binary file
            bit_array = BitArray(bin=padded_encoded_text)
            bit_array.tofile(output)

        print("Compression successful")
        return final_path

    # combines all decompressing functions above to turn a compressed binary file into a text file that should
    # replicate the original text file
    def decompress(self, encoded_path, output_file):
        final_path = output_file
        # encoding needed to be specified characters in different languages are recognised to be written to
        # a text file
        with open(encoded_path, 'rb') as file, open(final_path, 'w', encoding='utf-8') as output:
            # reads the bits in the binary file and stores into an array
            bit_string_array = BitArray(file.read())
            # gets the array back a a string of binary digits
            bit_string = bit_string_array.bin

            encoded_text = remove_padding(bit_string)

            decompressed_text = self.decoded_huffman_data(encoded_text)

            output.write(decompressed_text)

        print("Decompression successful")
        return final_path


# path1 = "first_english - Dead Star Rover.txt"
# binary_file1 = "dead_star_rover_english.bin"
# output_file1 = "dead_star_rover_decoded_file_english.txt"
#
# test1 = HuffmanCoding(path1)
#
# encoded_path1 = test1.compress(path1, binary_file1)
# print("Compressed file path: " + encoded_path1)
#
# decompressed_path1 = test1.decompress(encoded_path1, output_file1)
# print("Decompressed file path: " + decompressed_path1)
#
# path2 = "first_french - Dead Star Rover.en.fr.txt"
# binary_file2 = "dead_star_rover_french.bin"
# output_file2 = "dead_star_rover_decoded_file_french.txt"
#
# test2 = HuffmanCoding(path2)
#
# encoded_path2 = test2.compress(path2, binary_file2)
# print("Compressed file path: " + encoded_path2)
#
# decompressed_path2 = test2.decompress(encoded_path2, output_file2)
# print("Decompressed file path: " + decompressed_path2)
#
# path3 = "first_portuguese - Dead Star Rover.en.pt.txt"
# binary_file3 = "dead_star_rover_portuguese.bin"
# output_file3 = "dead_star_rover_decoded_file_portuguese.txt"
#
# test3 = HuffmanCoding(path3)
#
# encoded_path3 = test3.compress(path3, binary_file3)
# print("Compressed file path: " + encoded_path3)
#
# decompressed_path3 = test3.decompress(encoded_path3, output_file3)
# print("Decompressed file path: " + decompressed_path3)
#
# path4 = "second_english - The First Man on the Moon.txt"
# binary_file4 = "first_man_moon_english.bin"
# output_file4 = "first_man_moon_decoded_file_english.txt"
#
# test4 = HuffmanCoding(path4)
#
# encoded_path4 = test4.compress(path4, binary_file4)
# print("Compressed file path: " + encoded_path4)
#
# decompressed_path4 = test4.decompress(encoded_path4, output_file4)
# print("Decompressed file path: " + decompressed_path4)
#
# path5 = "second_french - The First Man on the Moon.en.fr.txt"
# binary_file5 = "first_man_moon_french.bin"
# output_file5 = "first_man_moon_decoded_file_french.txt"
#
# test5 = HuffmanCoding(path5)
#
# encoded_path5 = test5.compress(path5, binary_file5)
# print("Compressed file path: " + encoded_path5)
#
# decompressed_path5 = test5.decompress(encoded_path5, output_file5)
# print("Decompressed file path: " + decompressed_path5)
#
# path6 = "second_portuguese - The First Man on the Moon.en.pt.txt"
# binary_file6 = "first_man_moon_portuguese.bin"
# output_file6 = "first_man_moon_decoded_file_portuguese.txt"
#
# test6 = HuffmanCoding(path6)
#
# encoded_path6 = test6.compress(path6, binary_file6)
# print("Compressed file path: " + encoded_path6)
#
# decompressed_path6 = test6.decompress(encoded_path6, output_file6)
# print("Decompressed file path: " + decompressed_path6)

# path7 = "xaa.txt"
# binary_file7 = "einstein.en.bin"
# output_file7 = "einstein.en_decoded_file.txt"
#
# test7 = HuffmanCoding(path7)
#
# encoded_path7 = test7.compress(path7, binary_file7)
# print("Compressed file path: " + encoded_path7)
#
# decompressed_path7 = test7.decompress(encoded_path7, output_file7)
# print("Decompressed file path: " + decompressed_path7)

# path8 = "xaa3.txt"
# binary_file8 = "english.001.2.bin"
# output_file8 = "english.001.2_decoded_file.txt"
#
# test8 = HuffmanCoding(path8)
#
# encoded_path8 = test8.compress(path8, binary_file8)
# print("Compressed file path: " + encoded_path8)
#
# decompressed_path8 = test8.decompress(encoded_path8, output_file8)
# print("Decompressed file path: " + decompressed_path8)

# path9 = "xaa2.txt"
# binary_file9 = "rs.13.bin"
# output_file9 = "rs.13_decoded_file.txt"
#
# test9 = HuffmanCoding(path9)
#
# encoded_path9 = test9.compress(path9, binary_file9)
# print("Compressed file path: " + encoded_path9)
#
# decompressed_path9 = test9.decompress(encoded_path9, output_file9)
# print("Decompressed file path: " + decompressed_path9)
