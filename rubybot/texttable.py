def print_table(table, max_char):
    print(table)
    if table:
        if len(table) > 0:
            if len(table[0]) > 0:
                #find length/height
                col = len(table)
                row = len(table[0])
                maxlen = []
                output = []
                
                #find longest string per column
                for x in range(0, len(table[0])):
                    maxlen.append(0)
                    for y in range(0, len(table)):
                        maxlen[x] = max(len(str(table[y][x])), maxlen[x])

                print(maxlen)

                #construct the top/bottom of the table
                border = '+'
                for x in range(0, len(maxlen)):
                    border += '--'
                    border += maxlen[x] * '-'
                    border += '+'
                border += '\n'

                #check if the table goes over char limit
                if len(border) > max_char:
                    raise ValueError('Table is too big!')

                #add border to char limit
                output.append(border)

                #first row
                line = '|'
                for x in range(0, len(table[0])):

                    line += ' '

                    #add text
                    add = str(table[0][x])
                    blanks = maxlen[x] - len(add)
                    line += add

                    #add blanks
                    line += blanks * ' '

                    #add ending for that term
                    line += ' |'

                line += '\n'

                #add first data line
                if len(output[len(output) - 1]) + len(line) > max_char:
                    output.append(line)
                else:
                    output[len(output) - 1] += line

                #add another border
                if len(output[len(output) - 1]) + len(border) > max_char:
                    output.append(border)
                else:
                    output[len(output) - 1] += border

                #add remaining lines
                for x in range(1, len(table)):
                    add = '|'
                    for y in range(0, len(table[x])):

                        add += ' '

                        #add text
                        te = str(table[x][y])
                        blanks = maxlen[y] - len(te)
                        add += te

                        #add blanks
                        for z in range(0, blanks):
                            add += ' '

                        #add ending for that term
                        add += ' |'

                    add += '\n'
                    if len(output[len(output) - 1]) + len(add) > max_char:
                        output.append(add)
                    else:
                        output[len(output) - 1] += add

                #add final border
                if len(output[len(output) - 1]) + len(border) > max_char:
                    output.append(border)
                else:
                    output[len(output) - 1] += border

                return output
                
            else:
                raise TypeError('Table has no data!')
        else:
            raise TypeError('Table has no data!')
    else:
        raise TypeError('An invalid table was passed!')
'''
+----------------+----+
| LONGEST STRING | OK |
+----------------+----+
| LOL            |    |
| KEKKKKKKKKKKKK | K  |
+----------------+----+

'''

