* CMPL - Free-MPS - Export
NAME shortest-path
* OBJNAME costs
* OBJSENSE MIN
ROWS
 N costs
 E line_2
 E line_3
 E line_4
 E line_5
 E line_6
 E line_7
 E line_8
COLUMNS
 x[1,2] costs 7 line_2 1
 x[1,2] line_3 -1
 x[1,4] costs 5 line_2 1
 x[1,4] line_5 -1
 x[2,1] costs 7 line_2 -1
 x[2,1] line_3 1
 x[2,3] costs 8 line_3 1
 x[2,3] line_4 -1
 x[2,4] costs 9 line_3 1
 x[2,4] line_5 -1
 x[2,5] costs 7 line_3 1
 x[2,5] line_6 -1
 x[3,2] costs 8 line_3 -1
 x[3,2] line_4 1
 x[3,5] costs 5 line_4 1
 x[3,5] line_6 -1
 x[4,1] costs 5 line_2 -1
 x[4,1] line_5 1
 x[4,2] costs 9 line_3 -1
 x[4,2] line_5 1
 x[4,5] costs 15 line_5 1
 x[4,5] line_6 -1
 x[4,6] costs 6 line_5 1
 x[4,6] line_7 -1
 x[5,2] costs 7 line_3 -1
 x[5,2] line_6 1
 x[5,3] costs 5 line_4 -1
 x[5,3] line_6 1
 x[5,4] costs 15 line_5 -1
 x[5,4] line_6 1
 x[5,6] costs 8 line_6 1
 x[5,6] line_7 -1
 x[5,7] costs 9 line_6 1
 x[5,7] line_8 -1
 x[6,4] costs 6 line_5 -1
 x[6,4] line_7 1
 x[6,5] costs 8 line_6 -1
 x[6,5] line_7 1
 x[6,7] costs 11 line_7 1
 x[6,7] line_8 -1
 x[7,5] costs 9 line_6 -1
 x[7,5] line_8 1
 x[7,6] costs 11 line_7 -1
 x[7,6] line_8 1
RHS
 RHS line_2 1 line_8 -1
BOUNDS
 PL BOUND x[1,2]
 PL BOUND x[1,4]
 PL BOUND x[2,1]
 PL BOUND x[2,3]
 PL BOUND x[2,4]
 PL BOUND x[2,5]
 PL BOUND x[3,2]
 PL BOUND x[3,5]
 PL BOUND x[4,1]
 PL BOUND x[4,2]
 PL BOUND x[4,5]
 PL BOUND x[4,6]
 PL BOUND x[5,2]
 PL BOUND x[5,3]
 PL BOUND x[5,4]
 PL BOUND x[5,6]
 PL BOUND x[5,7]
 PL BOUND x[6,4]
 PL BOUND x[6,5]
 PL BOUND x[6,7]
 PL BOUND x[7,5]
 PL BOUND x[7,6]
ENDATA
