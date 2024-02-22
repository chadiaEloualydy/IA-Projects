with open( "./test.txt", "r") as f:
 print( [ ord( s ) for s in f.read() ])