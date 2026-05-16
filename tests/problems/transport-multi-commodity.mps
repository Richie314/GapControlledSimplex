* CMPL - Free-MPS - Export
NAME transport-multi-commodity
* OBJNAME costs
* OBJSENSE MIN
ROWS
 N costs
 E flows[W1,Gravel1]
 E flows[W1,Gravel2]
 E flows[U1,Gravel1]
 E flows[U1,Gravel2]
 E flows[U2,Gravel1]
 E flows[U2,Gravel2]
 E flows[W2,Gravel1]
 E flows[W2,Gravel2]
 E flows[W3,Gravel1]
 E flows[W3,Gravel2]
 E flows[U1a,Gravel1]
 E flows[U1a,Gravel2]
 E flows[B1,Gravel1]
 E flows[B1,Gravel2]
 E flows[B2,Gravel1]
 E flows[B2,Gravel2]
 E flows[B3,Gravel1]
 E flows[B3,Gravel2]
 E flows[B4,Gravel1]
 E flows[B4,Gravel2]
 E flows[U2a,Gravel1]
 E flows[U2a,Gravel2]
 G line_24
 G line_25
 G line_26
 G line_27
 G line_28
 G line_29
 G line_30
 G line_31
 G line_32
 G line_33
 G line_34
 G line_35
 G line_36
 G line_37
 G line_38
 G line_39
 L __line40
 L __line41
 L __line42
 L __line43
 L __line44
 L __line45
 L __line46
 L __line47
 L __line48
 L __line49
 L __line50
 L __line51
 L __line52
 L __line53
 L __line54
 L __line55
COLUMNS
 x[W1,U1,Gravel1] costs 35.000000 flows[W1,Gravel1] 1
 x[W1,U1,Gravel1] flows[U1,Gravel1] -1 line_24 1
 x[W1,U1,Gravel1] __line40 1
 x[W1,U1,Gravel2] costs 50.000000 flows[W1,Gravel2] 1
 x[W1,U1,Gravel2] flows[U1,Gravel2] -1 line_24 1
 x[W1,U1,Gravel2] __line40 1
 x[W1,U2,Gravel1] costs 72.000000 flows[W1,Gravel1] 1
 x[W1,U2,Gravel1] flows[U2,Gravel1] -1 line_25 1
 x[W1,U2,Gravel1] __line41 1
 x[W1,U2,Gravel2] costs 110.000000 flows[W1,Gravel2] 1
 x[W1,U2,Gravel2] flows[U2,Gravel2] -1 line_25 1
 x[W1,U2,Gravel2] __line41 1
 x[U1,U1a,Gravel1] flows[U1,Gravel1] 1 flows[U1a,Gravel1] -1
 x[U1,U1a,Gravel1] line_26 1 __line42 1
 x[U1,U1a,Gravel2] flows[U1,Gravel2] 1 flows[U1a,Gravel2] -1
 x[U1,U1a,Gravel2] line_26 1 __line42 1
 x[U2,U2a,Gravel1] flows[U2,Gravel1] 1 flows[U2a,Gravel1] -1
 x[U2,U2a,Gravel1] line_27 1 __line43 1
 x[U2,U2a,Gravel2] flows[U2,Gravel2] 1 flows[U2a,Gravel2] -1
 x[U2,U2a,Gravel2] line_27 1 __line43 1
 x[W2,U1,Gravel1] costs 52.000000 flows[U1,Gravel1] -1
 x[W2,U1,Gravel1] flows[W2,Gravel1] 1 line_28 1
 x[W2,U1,Gravel1] __line44 1
 x[W2,U1,Gravel2] costs 77.000000 flows[U1,Gravel2] -1
 x[W2,U1,Gravel2] flows[W2,Gravel2] 1 line_28 1
 x[W2,U1,Gravel2] __line44 1
 x[W2,U2,Gravel1] costs 49.000000 flows[U2,Gravel1] -1
 x[W2,U2,Gravel1] flows[W2,Gravel1] 1 line_29 1
 x[W2,U2,Gravel1] __line45 1
 x[W2,U2,Gravel2] costs 72.000000 flows[U2,Gravel2] -1
 x[W2,U2,Gravel2] flows[W2,Gravel2] 1 line_29 1
 x[W2,U2,Gravel2] __line45 1
 x[W3,U1,Gravel1] costs 62.000000 flows[U1,Gravel1] -1
 x[W3,U1,Gravel1] flows[W3,Gravel1] 1 line_30 1
 x[W3,U1,Gravel1] __line46 1
 x[W3,U1,Gravel2] costs 94.000000 flows[U1,Gravel2] -1
 x[W3,U1,Gravel2] flows[W3,Gravel2] 1 line_30 1
 x[W3,U1,Gravel2] __line46 1
 x[W3,U2,Gravel1] costs 38.000000 flows[U2,Gravel1] -1
 x[W3,U2,Gravel1] flows[W3,Gravel1] 1 line_31 1
 x[W3,U2,Gravel1] __line47 1
 x[W3,U2,Gravel2] costs 55.000000 flows[U2,Gravel2] -1
 x[W3,U2,Gravel2] flows[W3,Gravel2] 1 line_31 1
 x[W3,U2,Gravel2] __line47 1
 x[U1a,B1,Gravel1] costs 86.000000 flows[U1a,Gravel1] 1
 x[U1a,B1,Gravel1] flows[B1,Gravel1] -1 line_32 1
 x[U1a,B1,Gravel1] __line48 1
 x[U1a,B1,Gravel2] costs 134.000000 flows[U1a,Gravel2] 1
 x[U1a,B1,Gravel2] flows[B1,Gravel2] -1 line_32 1
 x[U1a,B1,Gravel2] __line48 1
 x[U1a,B2,Gravel1] costs 43.000000 flows[U1a,Gravel1] 1
 x[U1a,B2,Gravel1] flows[B2,Gravel1] -1 line_33 1
 x[U1a,B2,Gravel1] __line49 1
 x[U1a,B2,Gravel2] costs 63.000000 flows[U1a,Gravel2] 1
 x[U1a,B2,Gravel2] flows[B2,Gravel2] -1 line_33 1
 x[U1a,B2,Gravel2] __line49 1
 x[U1a,B3,Gravel1] costs 48.000000 flows[U1a,Gravel1] 1
 x[U1a,B3,Gravel1] flows[B3,Gravel1] -1 line_34 1
 x[U1a,B3,Gravel1] __line50 1
 x[U1a,B3,Gravel2] costs 71.000000 flows[U1a,Gravel2] 1
 x[U1a,B3,Gravel2] flows[B3,Gravel2] -1 line_34 1
 x[U1a,B3,Gravel2] __line50 1
 x[U1a,B4,Gravel1] costs 37.000000 flows[U1a,Gravel1] 1
 x[U1a,B4,Gravel1] flows[B4,Gravel1] -1 line_35 1
 x[U1a,B4,Gravel1] __line51 1
 x[U1a,B4,Gravel2] costs 53.000000 flows[U1a,Gravel2] 1
 x[U1a,B4,Gravel2] flows[B4,Gravel2] -1 line_35 1
 x[U1a,B4,Gravel2] __line51 1
 x[U2a,B1,Gravel1] costs 34.000000 flows[B1,Gravel1] -1
 x[U2a,B1,Gravel1] flows[U2a,Gravel1] 1 line_36 1
 x[U2a,B1,Gravel1] __line52 1
 x[U2a,B1,Gravel2] costs 48.000000 flows[B1,Gravel2] -1
 x[U2a,B1,Gravel2] flows[U2a,Gravel2] 1 line_36 1
 x[U2a,B1,Gravel2] __line52 1
 x[U2a,B2,Gravel1] costs 96.000000 flows[B2,Gravel1] -1
 x[U2a,B2,Gravel1] flows[U2a,Gravel1] 1 line_37 1
 x[U2a,B2,Gravel1] __line53 1
 x[U2a,B2,Gravel2] costs 152.000000 flows[B2,Gravel2] -1
 x[U2a,B2,Gravel2] flows[U2a,Gravel2] 1 line_37 1
 x[U2a,B2,Gravel2] __line53 1
 x[U2a,B3,Gravel1] costs 103.000000 flows[B3,Gravel1] -1
 x[U2a,B3,Gravel1] flows[U2a,Gravel1] 1 line_38 1
 x[U2a,B3,Gravel1] __line54 1
 x[U2a,B3,Gravel2] costs 164.000000 flows[B3,Gravel2] -1
 x[U2a,B3,Gravel2] flows[U2a,Gravel2] 1 line_38 1
 x[U2a,B3,Gravel2] __line54 1
 x[U2a,B4,Gravel1] costs 21.000000 flows[B4,Gravel1] -1
 x[U2a,B4,Gravel1] flows[U2a,Gravel1] 1 line_39 1
 x[U2a,B4,Gravel1] __line55 1
 x[U2a,B4,Gravel2] costs 28.000000 flows[B4,Gravel2] -1
 x[U2a,B4,Gravel2] flows[U2a,Gravel2] 1 line_39 1
 x[U2a,B4,Gravel2] __line55 1
RHS
 RHS flows[W1,Gravel1] 35.000000 flows[W1,Gravel2] 40.000000
 RHS flows[W2,Gravel1] 40.000000 flows[W2,Gravel2] 50.000000
 RHS flows[W3,Gravel1] 25.000000 flows[W3,Gravel2] 30.000000
 RHS flows[B1,Gravel1] -25.000000 flows[B1,Gravel2] -30.000000
 RHS flows[B2,Gravel1] -20.000000 flows[B2,Gravel2] -15.000000
 RHS flows[B3,Gravel1] -40.000000 flows[B3,Gravel2] -50.000000
 RHS flows[B4,Gravel1] -15.000000 flows[B4,Gravel2] -25.000000
 RHS __line40 50.000000 __line41 50.000000
 RHS __line42 120.000000 __line43 120.000000
 RHS __line44 50.000000 __line45 50.000000
 RHS __line46 50.000000 __line47 50.000000
 RHS __line48 50.000000 __line49 50.000000
 RHS __line50 50.000000 __line51 50.000000
 RHS __line52 40.000000 __line53 40.000000
 RHS __line54 40.000000 __line55 40.000000
BOUNDS
 PL BOUND x[W1,U1,Gravel1]
 PL BOUND x[W1,U1,Gravel2]
 PL BOUND x[W1,U2,Gravel1]
 PL BOUND x[W1,U2,Gravel2]
 PL BOUND x[U1,U1a,Gravel1]
 PL BOUND x[U1,U1a,Gravel2]
 PL BOUND x[U2,U2a,Gravel1]
 PL BOUND x[U2,U2a,Gravel2]
 PL BOUND x[W2,U1,Gravel1]
 PL BOUND x[W2,U1,Gravel2]
 PL BOUND x[W2,U2,Gravel1]
 PL BOUND x[W2,U2,Gravel2]
 PL BOUND x[W3,U1,Gravel1]
 PL BOUND x[W3,U1,Gravel2]
 PL BOUND x[W3,U2,Gravel1]
 PL BOUND x[W3,U2,Gravel2]
 PL BOUND x[U1a,B1,Gravel1]
 PL BOUND x[U1a,B1,Gravel2]
 PL BOUND x[U1a,B2,Gravel1]
 PL BOUND x[U1a,B2,Gravel2]
 PL BOUND x[U1a,B3,Gravel1]
 PL BOUND x[U1a,B3,Gravel2]
 PL BOUND x[U1a,B4,Gravel1]
 PL BOUND x[U1a,B4,Gravel2]
 PL BOUND x[U2a,B1,Gravel1]
 PL BOUND x[U2a,B1,Gravel2]
 PL BOUND x[U2a,B2,Gravel1]
 PL BOUND x[U2a,B2,Gravel2]
 PL BOUND x[U2a,B3,Gravel1]
 PL BOUND x[U2a,B3,Gravel2]
 PL BOUND x[U2a,B4,Gravel1]
 PL BOUND x[U2a,B4,Gravel2]
ENDATA
