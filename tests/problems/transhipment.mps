* CMPL - Free-MPS - Export
NAME transhipment
* OBJNAME costs
* OBJSENSE MIN
ROWS
 N costs
 E flowCon[H]
 E flowCon[Z1]
 E flowCon[Z2]
 E flowCon[Z3]
 E flowCon[W1]
 E flowCon[W2]
 E flowCon[W3]
 E flowCon[Z1a]
 E flowCon[R1]
 E flowCon[R2]
 E flowCon[R3]
 E flowCon[R4]
 E flowCon[Z2a]
 E flowCon[Z3a]
 E flowCon[R1a]
 E flowCon[D1]
 E flowCon[D2]
 E flowCon[D3]
 E flowCon[D4]
 E flowCon[D5]
 E flowCon[R2a]
 E flowCon[D6]
 E flowCon[D7]
 E flowCon[R3a]
 E flowCon[R4a]
COLUMNS
 x[H,Z1] costs 25.000000 flowCon[H] 1
 x[H,Z1] flowCon[Z1] -1
 x[H,Z2] costs 45.000000 flowCon[H] 1
 x[H,Z2] flowCon[Z2] -1
 x[H,Z3] costs 60.000000 flowCon[H] 1
 x[H,Z3] flowCon[Z3] -1
 x[Z1,Z1a] flowCon[Z1] 1 flowCon[Z1a] -1
 x[Z2,Z2a] flowCon[Z2] 1 flowCon[Z2a] -1
 x[Z3,Z3a] flowCon[Z3] 1 flowCon[Z3a] -1
 x[W1,Z1] costs 12.000000 flowCon[Z1] -1
 x[W1,Z1] flowCon[W1] 1
 x[W1,Z2] costs 50.000000 flowCon[Z2] -1
 x[W1,Z2] flowCon[W1] 1
 x[W1,Z3] costs 36.000000 flowCon[Z3] -1
 x[W1,Z3] flowCon[W1] 1
 x[W2,Z1] costs 110.000000 flowCon[Z1] -1
 x[W2,Z1] flowCon[W2] 1
 x[W2,Z2] costs 62.000000 flowCon[Z2] -1
 x[W2,Z2] flowCon[W2] 1
 x[W2,Z3] costs 54.000000 flowCon[Z3] -1
 x[W2,Z3] flowCon[W2] 1
 x[W3,Z1] costs 30.000000 flowCon[Z1] -1
 x[W3,Z1] flowCon[W3] 1
 x[W3,Z2] costs 24.000000 flowCon[Z2] -1
 x[W3,Z2] flowCon[W3] 1
 x[W3,Z3] costs 28.000000 flowCon[Z3] -1
 x[W3,Z3] flowCon[W3] 1
 x[Z1a,R1] costs 15.000000 flowCon[Z1a] 1
 x[Z1a,R1] flowCon[R1] -1
 x[Z1a,R2] costs 18.000000 flowCon[Z1a] 1
 x[Z1a,R2] flowCon[R2] -1
 x[Z1a,R3] costs 24.000000 flowCon[Z1a] 1
 x[Z1a,R3] flowCon[R3] -1
 x[Z1a,R4] costs 20.000000 flowCon[Z1a] 1
 x[Z1a,R4] flowCon[R4] -1
 x[R1,R1a] flowCon[R1] 1 flowCon[R1a] -1
 x[R2,R2a] flowCon[R2] 1 flowCon[R2a] -1
 x[R3,R3a] flowCon[R3] 1 flowCon[R3a] -1
 x[R4,R4a] flowCon[R4] 1 flowCon[R4a] -1
 x[Z2a,R1] costs 28.000000 flowCon[R1] -1
 x[Z2a,R1] flowCon[Z2a] 1
 x[Z2a,R2] costs 30.000000 flowCon[R2] -1
 x[Z2a,R2] flowCon[Z2a] 1
 x[Z2a,R3] costs 22.000000 flowCon[R3] -1
 x[Z2a,R3] flowCon[Z2a] 1
 x[Z2a,R4] costs 12.000000 flowCon[R4] -1
 x[Z2a,R4] flowCon[Z2a] 1
 x[Z3a,R1] costs 22.000000 flowCon[R1] -1
 x[Z3a,R1] flowCon[Z3a] 1
 x[Z3a,R2] costs 14.000000 flowCon[R2] -1
 x[Z3a,R2] flowCon[Z3a] 1
 x[Z3a,R3] costs 16.000000 flowCon[R3] -1
 x[Z3a,R3] flowCon[Z3a] 1
 x[Z3a,R4] costs 8.000000 flowCon[R4] -1
 x[Z3a,R4] flowCon[Z3a] 1
 x[R1a,D1] costs 60.000000 flowCon[R1a] 1
 x[R1a,D1] flowCon[D1] -1
 x[R1a,D2] costs 52.000000 flowCon[R1a] 1
 x[R1a,D2] flowCon[D2] -1
 x[R1a,D3] costs 70.000000 flowCon[R1a] 1
 x[R1a,D3] flowCon[D3] -1
 x[R1a,D4] costs 60.000000 flowCon[R1a] 1
 x[R1a,D4] flowCon[D4] -1
 x[R1a,D5] costs 40.000000 flowCon[R1a] 1
 x[R1a,D5] flowCon[D5] -1
 x[R2a,D1] costs 110.000000 flowCon[D1] -1
 x[R2a,D1] flowCon[R2a] 1
 x[R2a,D2] costs 84.000000 flowCon[D2] -1
 x[R2a,D2] flowCon[R2a] 1
 x[R2a,D3] costs 15.000000 flowCon[D3] -1
 x[R2a,D3] flowCon[R2a] 1
 x[R2a,D4] costs 28.000000 flowCon[D4] -1
 x[R2a,D4] flowCon[R2a] 1
 x[R2a,D6] costs 42.000000 flowCon[R2a] 1
 x[R2a,D6] flowCon[D6] -1
 x[R2a,D7] costs 120.000000 flowCon[R2a] 1
 x[R2a,D7] flowCon[D7] -1
 x[R3a,D1] costs 200.000000 flowCon[D1] -1
 x[R3a,D1] flowCon[R3a] 1
 x[R3a,D2] costs 72.000000 flowCon[D2] -1
 x[R3a,D2] flowCon[R3a] 1
 x[R3a,D3] costs 42.000000 flowCon[D3] -1
 x[R3a,D3] flowCon[R3a] 1
 x[R3a,D4] costs 18.000000 flowCon[D4] -1
 x[R3a,D4] flowCon[R3a] 1
 x[R3a,D5] costs 30.000000 flowCon[D5] -1
 x[R3a,D5] flowCon[R3a] 1
 x[R3a,D6] costs 50.000000 flowCon[D6] -1
 x[R3a,D6] flowCon[R3a] 1
 x[R3a,D7] costs 60.000000 flowCon[D7] -1
 x[R3a,D7] flowCon[R3a] 1
 x[R4a,D1] costs 140.000000 flowCon[D1] -1
 x[R4a,D1] flowCon[R4a] 1
 x[R4a,D2] costs 74.000000 flowCon[D2] -1
 x[R4a,D2] flowCon[R4a] 1
 x[R4a,D4] costs 45.000000 flowCon[D4] -1
 x[R4a,D4] flowCon[R4a] 1
 x[R4a,D5] costs 20.000000 flowCon[D5] -1
 x[R4a,D5] flowCon[R4a] 1
 x[R4a,D7] costs 110.000000 flowCon[D7] -1
 x[R4a,D7] flowCon[R4a] 1
RHS
 RHS flowCon[H] 320.000000 flowCon[W1] 500.000000
 RHS flowCon[W2] 260.000000 flowCon[W3] 120.000000
 RHS flowCon[D1] -120.000000 flowCon[D2] -240.000000
 RHS flowCon[D3] -80.000000 flowCon[D4] -280.000000
 RHS flowCon[D5] -160.000000 flowCon[D6] -180.000000
 RHS flowCon[D7] -140.000000
BOUNDS
 UP BOUND x[H,Z1] 170.000000
 UP BOUND x[H,Z2] 170.000000
 UP BOUND x[H,Z3] 170.000000
 UP BOUND x[Z1,Z1a] 600.000000
 UP BOUND x[Z2,Z2a] 400.000000
 UP BOUND x[Z3,Z3a] 500.000000
 UP BOUND x[W1,Z1] 170.000000
 UP BOUND x[W1,Z2] 170.000000
 UP BOUND x[W1,Z3] 170.000000
 UP BOUND x[W2,Z1] 170.000000
 UP BOUND x[W2,Z2] 170.000000
 UP BOUND x[W2,Z3] 170.000000
 UP BOUND x[W3,Z1] 170.000000
 UP BOUND x[W3,Z2] 170.000000
 UP BOUND x[W3,Z3] 170.000000
 UP BOUND x[Z1a,R1] 170.000000
 UP BOUND x[Z1a,R2] 170.000000
 UP BOUND x[Z1a,R3] 170.000000
 UP BOUND x[Z1a,R4] 170.000000
 UP BOUND x[R1,R1a] 400.000000
 UP BOUND x[R2,R2a] 200.000000
 UP BOUND x[R3,R3a] 500.000000
 UP BOUND x[R4,R4a] 300.000000
 UP BOUND x[Z2a,R1] 170.000000
 UP BOUND x[Z2a,R2] 170.000000
 UP BOUND x[Z2a,R3] 170.000000
 UP BOUND x[Z2a,R4] 170.000000
 UP BOUND x[Z3a,R1] 170.000000
 UP BOUND x[Z3a,R2] 170.000000
 UP BOUND x[Z3a,R3] 170.000000
 UP BOUND x[Z3a,R4] 170.000000
 UP BOUND x[R1a,D1] 170.000000
 UP BOUND x[R1a,D2] 170.000000
 UP BOUND x[R1a,D3] 170.000000
 UP BOUND x[R1a,D4] 170.000000
 UP BOUND x[R1a,D5] 170.000000
 UP BOUND x[R2a,D1] 170.000000
 UP BOUND x[R2a,D2] 170.000000
 UP BOUND x[R2a,D3] 170.000000
 UP BOUND x[R2a,D4] 170.000000
 UP BOUND x[R2a,D6] 170.000000
 UP BOUND x[R2a,D7] 170.000000
 UP BOUND x[R3a,D1] 170.000000
 UP BOUND x[R3a,D2] 170.000000
 UP BOUND x[R3a,D3] 170.000000
 UP BOUND x[R3a,D4] 170.000000
 UP BOUND x[R3a,D5] 170.000000
 UP BOUND x[R3a,D6] 170.000000
 UP BOUND x[R3a,D7] 170.000000
 UP BOUND x[R4a,D1] 170.000000
 UP BOUND x[R4a,D2] 170.000000
 UP BOUND x[R4a,D4] 170.000000
 UP BOUND x[R4a,D5] 170.000000
 UP BOUND x[R4a,D7] 170.000000
ENDATA
