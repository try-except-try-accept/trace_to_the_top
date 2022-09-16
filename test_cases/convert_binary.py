

def convert_binary(bina):

    lsb = len(bina)-1
    msb = 0
    col = 1
    tot = 0

    for i in range(lsb, msb-1, -1):
        bit = int(bina[i])
        tot += bit * col
        col = col * 2

    return tot


a = convert_binary("101101")
b = convert_binary("1001")
c = convert_binary("1101")
d = convert_binary("101101011")
print("Converted your binary numbers: ")
print(a, b, c, d)

            


    
