from pysgf import SGF
import os


def is_a_leaf(node):
    if len(node.properties['C']) > 0:
        comment = node.properties['C'][0].lower()
        if comment.startswith('correct') or comment.startswith('wrong'):
            return True
    if len(node.children) == 0:
        return True
    return False


def get_sgf_from_node_to_leaf(root, isFirst=False):
    if isFirst:
        sgf = ""
    else:
        sgf = node_to_sgf(root)
    if is_a_leaf(root):
        return sgf
    if len(root.children) == 1:
        sgf += get_sgf_from_node_to_leaf(root.children[0])
    if len(root.children) > 1:
        for child in root.children:
            sgf += "(" + get_sgf_from_node_to_leaf(child)+")"

    return sgf


def node_to_sgf(node, dont_include=[]):
    sgf = ";"
    sgf += properties_to_sgf_format(node.properties, dont_include)

    return sgf


def properties_to_sgf_format(properties, dont_include=[]):
    sgf = ""
    for key in properties:
        if key not in dont_include:
            values = properties[key]
            if len(values) != 0:
                sgf += key

                for v in values:
                    sgf += "["+v+"]"

    return sgf


def generate_sgf_from(node):

    sgf = "(;"+properties_to_sgf_format(
        node.nodes_from_root[0].properties, dont_include=["C"])

    for n in node.nodes_from_root[1:] + [node]:
        for move in n.move_with_placements:
            sgfcoord = move.sgf(node.board_size)
            if move.player == 'W':
                sgf += "AW["+sgfcoord+"]"
            if move.player == 'B':
                sgf += "AB["+sgfcoord+"]"
    sgf += properties_to_sgf_format(node.properties, dont_include=["B", "W"])

    sgf += get_sgf_from_node_to_leaf(node, isFirst=True)+")"

    return sgf


def split_problems(path, problem_indicator):
    return_sgfs = []
    root = SGF.parse_file(path)
    current = root
    currentProblem = None
    leafs = []
    filename = os.path.split(path)[-1]
    open = [root]
    while len(open) > 0:
        current = open.pop()
        if current.properties["C"] and current.properties["C"][0].startswith(problem_indicator):

            current.properties['C'] = current.properties['C'][0][len(problem_indicator):]
            currentProblem = current
            sgf = generate_sgf_from(currentProblem)
            return_sgfs.append(sgf)
        open += current.children
    return return_sgfs


nb_digit_filename = 4
input_dir = os.path.join(".", "sgfs")
output_dir = os.path.join(".", "problems")
problem_indicator_prefix = "P "

if(not os.path.exists(input_dir)):
    os.makedirs(input_dir)

if(not os.path.exists(output_dir)):
    os.makedirs(output_dir)
for root, dirs, files in os.walk(input_dir, topdown=False):

    for name in files:
        just_name = name.split(".")[0]
        path = os.path.join(root, name)
        print("opening: "+path)
        sgfs = split_problems(path, problem_indicator_prefix)

        for index in range(len(sgfs)):
            sgf = sgfs[index]
            problem_number_string = str(index+1)
            string_zeros = "0"*(nb_digit_filename-len(problem_number_string))

            problem_number_string = string_zeros + problem_number_string
            probleme_name = just_name+" " + problem_number_string+".sgf"
            path_problem = os.path.join(output_dir, probleme_name)
            f = open(path_problem, "w", encoding="utf-8")
            f.write(sgf)
            print("created problem: " + path_problem)
