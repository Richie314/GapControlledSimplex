* CMPL - Free-MPS - Export
NAME transportation
* OBJNAME costs
* OBJSENSE MIN
ROWS
 N costs
 E line_2
 E line_3
 E line_4
 L line_5
 L line_6
 L line_7
 L line_8
COLUMNS
 x[1,1] costs 3 line_2 1
 x[1,1] line_5 1
 x[1,2] costs 2 line_2 1
 x[1,2] line_6 1
 x[1,4] costs 6 line_2 1
 x[1,4] line_8 1
 x[2,2] costs 5 line_3 1
 x[2,2] line_6 1
 x[2,3] costs 2 line_3 1
 x[2,3] line_7 1
 x[2,4] costs 3 line_3 1
 x[2,4] line_8 1
 x[3,1] costs 2 line_4 1
 x[3,1] line_5 1
 x[3,3] costs 4 line_4 1
 x[3,3] line_7 1
RHS
 RHS line_2 5000 line_3 6000
 RHS line_4 2500 line_5 6000
 RHS line_6 4000 line_7 2000
 RHS line_8 1500
BOUNDS
 PL BOUND x[1,1]
 PL BOUND x[1,2]
 PL BOUND x[1,4]
 PL BOUND x[2,2]
 PL BOUND x[2,3]
 PL BOUND x[2,4]
 PL BOUND x[3,1]
 PL BOUND x[3,3]
ENDATA
