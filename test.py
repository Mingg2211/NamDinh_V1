lines = [line for line in open('data\procedure.txt','r',encoding='utf-8')]
print(len(lines))
print(lines[:5])
f = open('data/new_procedure.txt','w', encoding='utf-8')
for line in lines:
    line = line.rstrip()
    f.write(line+'\t'+line)
    f.write('\n')
# import pandas as pd
# df = pd.read_csv('data/new_procedure.csv')
# print(df.head)