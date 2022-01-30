import csv

data_path = "data_4.csv"

icp_id = 4

julia_file = open(str(icp_id) + ".jl", "w")

julia_file.write("import Rotations\n")
julia_file.write("import LinearAlgebra\n")
julia_file.write("using Test\n")
julia_file.write("using Posegraph\n")

julia_file.write("graph = Graph()\n")

julia_file.write("\n")
julia_file.write("\n")
julia_file.write("\n")


line_count = 0
with open(data_path, "r") as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=",")
    for row in csv_reader:
        data_row = None
        if line_count == 0:
            headers = row
            line_count += 1
            continue
        else:
            data_row = row
            new_julia_line = ("p" + str(line_count) + " = Float64[" +
                str(data_row[3]) + "," +
                str(data_row[4]) + "," +
                str(data_row[5]) + "]" + "\n"
            )
            julia_file.write(new_julia_line)

            new_julia_line_2 = ("q" + str(line_count) + " = Float64[" +
                str(data_row[0]) + "," +
                str(data_row[1]) + "," +
                str(data_row[2]) + "]" + "\n"
            )
            julia_file.write(new_julia_line_2)
            line_count += 1

julia_file.write("\n\n\n")

julia_file.write("T = Matrix{Float64}(LinearAlgebra.I, 4, 4)\n")
julia_file.write("se3_v = VertexSE3(\"Tdst_src\", T)\n")
julia_file.write("add_vertex!(graph, se3_v)\n")

julia_file.write("\n\n\n")

for i in range(1, line_count):
    julia_file.write("pe_" + str(i) + " = Point3DistanceError(se3_v,p" + str(i) + ", q" + str(i) + ")\n")
    julia_file.write("add_edge!(graph, pe_" + str(i) + ")\n\n")

julia_file.write("solve!(graph)\n")
julia_file.write("T = getT(se3_v)\n")
julia_file.write("println(T)\n")


            # julia_file.write("p" + str(line_count) + " = Float64[" +
            #     str(data_row[3]) + "," +
            #     str(data_row[4]) + "," +
            #     str(data_row[5]) + "]"
            # )

