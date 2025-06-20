*load ETH - Daily
*Take combined V2
gen LiquidityS = Liquidity / 1000
summarize ABSdailyvolumeETH Tradesperday LiquidityS tradesize
outreg2 using "summary_tableETH2.doc", replace sum(log) keep(ABSdailyvolumeETH Tradesperday LiquidityS tradesize) word
shellout using `"summary_tableETH1.doc"'

*Take combined V3
gen LiquidityS = Avgliq / 1000
summarize ABSdailyvolumeETH Tradesperday LiquidityS Medliq tradesize
outreg2 using "summary_tableETH3.doc", replace sum(log) keep(ABSdailyvolumeETH Tradesperday LiquidityS tradesize) word
shellout using `"summary_tableETH2.doc"'

*load PEPE - Daily
*Take combined V2
gen LiquidityS = Liquidity / 1000
summarize ABSdailyvolumeETH Tradesperday LiquidityS tradesize
outreg2 using "summary_tablePEPE2.doc", replace sum(log) keep(ABSdailyvolumeETH Tradesperday LiquidityS tradesize) word
shellout using `"summary_tablePEPE2.doc"'

*Take combined V3
gen LiquidityS = Avgliq / 1000
summarize ABSdailyvolumeETH Tradesperday LiquidityS Medliq tradesize
outreg2 using "summary_tablePEPE3.doc", replace sum(log) keep(ABSdailyvolumeETH Tradesperday LiquidityS tradesize) word
shellout using `"summary_tablePEPE3.doc"'


*Relative ETH
summarize r_priceimpact r_standliq_AVG r_assym r_noisetrades r_srandnoisereversal r_standfees_TVL, detail
outreg2 using "summary_tableETH4.doc", replace sum(log) keep(r_priceimpact r_standliq_AVG r_assym r_noisetrades r_srandnoisereversal r_standfees_TVL) word
shellout using `"summary_tableETH4.doc"'

*Relative PEPE
summarize r_priceimpact r_standliq_AVG r_assym r_noisetrades r_srandnoisereversal r_standfees_TVL, detail
outreg2 using "summary_tablePEPE4.doc", replace sum(log) keep(r_priceimpact r_standliq_AVG r_assym r_noisetrades r_srandnoisereversal r_standfees_TVL) word
shellout using `"summary_tablePEPE4.doc"'


*ETH V2
summarize Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
outreg2 using "summary_tableETH5.doc", replace sum(log) keep(Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact) word
shellout using `"summary_tableETH5.doc"'

*ETH V3
summarize Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
outreg2 using "summary_tableETH6.doc", replace sum(log) keep(Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact) word
shellout using `"summary_tableETH6.doc"'

*PEPE V2
gen Vola = AnnualizedSD / 1000
summarize Gaschanges Orderimbalances Vola Marketreturn Depthchanges Liqpriceimpact
outreg2 using "summary_tablePEPE5.doc", replace sum(log) keep(Gaschanges Orderimbalances Vola Marketreturn Depthchanges Liqpriceimpact) word
shellout using `"summary_tablePEPE5.doc"'

*PEPE V3
gen Vola = AnnualizedSD / 1000
summarize Gaschanges Orderimbalances Vola Marketreturn Depthchanges Liqpriceimpact
outreg2 using "summary_tablePEPE6.doc", replace sum(log) keep(Gaschanges Orderimbalances Vola Marketreturn Depthchanges Liqpriceimpact) word
shellout using `"summary_tablePEPE6.doc"'

*stationarity / normality tests via Python




*ETH
*Hypothesis 1
regress r_standliq_AVG r_assym r_srandnoisereversal r_standfees_TVL
regress r_standliq_AVG r_assym r_noisetrades r_standfees_TVL

newey2 r_standliq_AVG r_assym r_standfees_TVL r_srandnoisereversal, lag(7) force
outreg2 using "~/Desktop/results1.doc", append dec(2) ctitle(Model 1)
newey2 r_standliq_AVG r_assym r_standfees_TVL r_noisetrades, lag(7) force
outreg2 using "~/Desktop/results1.doc", append dec(2) ctitle(Model 3)

*Hypothesis 2
regress r_priceimpact r_assym r_srandnoisereversal r_standfees_TVL 
regress r_priceimpact r_assym r_noisetrades r_standfees_TVL 

newey2 r_priceimpact r_assym r_srandnoisereversal r_standfees_TVL , lag(7) force
outreg2 using "~/Desktop/results2.doc", append dec(3) ctitle(Model 1)
newey2 r_priceimpact r_assym r_noisetrades r_standfees_TVL, lag(7) force
outreg2 using "~/Desktop/results2.doc", append dec(3) ctitle(Model 3)


*PEPE
*Hypothesis 1
regress r_standliq_AVG r_assym r_srandnoisereversal r_standfees_TVL
regress r_standliq_AVG r_assym r_noisetrades r_standfees_TVL

newey2 r_standliq_AVG r_assym r_standfees_TVL r_srandnoisereversal, lag(6) force
outreg2 using "~/Desktop/results3.doc", append dec(2) ctitle(Model 1)
newey2 r_standliq_AVG r_assym r_standfees_TVL r_noisetrades, lag(6) force
outreg2 using "~/Desktop/results3.doc", append dec(2) ctitle(Model 3)

*Hypothesis 2
regress r_priceimpact r_assym r_srandnoisereversal r_standfees_TVL 
regress r_priceimpact r_assym r_noisetrades r_standfees_TVL 

newey2 r_priceimpact r_assym r_srandnoisereversal r_standfees_TVL , lag(6) force
outreg2 using "~/Desktop/results4.doc", append dec(3) ctitle(Model 1)
newey2 r_priceimpact r_assym r_noisetrades r_standfees_TVL, lag(6) force
outreg2 using "~/Desktop/results4.doc", append dec(3) ctitle(Model 3)



*Graph
twoway (line r_priceimpact Date if Pool=="PEPE", sort lcolor(blue) lpattern(solid) legend(label(1 "PEPE"))) (line r_priceimpact_Hour Date if Pool=="ETH",  sort lcolor(red)  lpattern(solid) legend(label(2 "ETH"))), title("Price impact by Pool") xtitle(Date) ytitle("Relative Price Impact") legend(order(1 2) rows(1) ring(1) pos(6))

twoway (line r_standliq_AVG Date if Pool=="PEPE", sort lcolor(blue) lpattern(solid) legend(label(1 "PEPE"))) (line r_standliq_AVG Date if Pool=="ETH",  sort lcolor(red)  lpattern(solid) legend(label(2 "ETH"))), title("Standardized Liquidity by Pool") xtitle(Date) ytitle("Relative Standardized Liquidity") legend(order(1 2) rows(1) ring(1) pos(6))
	

	
*Cholesky decomposition


*Corr error term
*price impact
varsoc Orderimbalances AnnualizedSD Marketreturn Liqpriceimpact
//change amount of lags
var Orderimbalances AnnualizedSD Marketreturn Liqpriceimpact, lags(1/3)	

predict resid_ORD, resid eq(Orderimbalances)
predict resid_VOL, resid eq(AnnualizedSD)
predict resid_RET, resid eq(Marketreturn)
predict resid_IMP, resid eq(Liqpriceimpact)
corr resid_ORD resid_VOL resid_RET resid_IMP

*liquidity depth
varsoc Orderimbalances AnnualizedSD Marketreturn Depthchanges
//change amount of lags
var Orderimbalances AnnualizedSD Marketreturn Depthchanges, lags(1/3)	

predict resid_ORD2, resid eq(Orderimbalances)
predict resid_VOL2, resid eq(AnnualizedSD)
predict resid_RET2, resid eq(Marketreturn)
predict resid_DEP2, resid eq(Depthchanges)
corr resid_ORD2 resid_VOL2 resid_RET2 resid_DEP2

*Granger endogenous variables (liq always most endogenous)
	
*Order-Market
varsoc Marketreturn Orderimbalances	

var Marketreturn Orderimbalances, lags(1/1)
vargranger
	
*VOL-market	
varsoc Marketreturn AnnualizedSD	

var Marketreturn AnnualizedSD, lags(1/3)
vargranger

*Order-Vol
varsoc AnnualizedSD Orderimbalances	

var AnnualizedSD Orderimbalances, lags(1/3)
vargranger



*Liq-dept
varsoc Depthchanges Liqpriceimpact	

var Depthchanges Liqpriceimpact, lags(1/3)
vargranger
	
	
	
	
*VAR
*V2 ETH/USDC
varsoc Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
var Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact, lags(1/1)
varstable
irf create V2, replace step(12) set(myirf)
irf graph irf, irf(V2) impulse(Orderimbalances AnnualizedSD Marketreturn) response(Depthchanges Liqpriceimpact)

*V3 ETH/UDSDC
varsoc Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
var Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact, lags(1/1)
varstable
irf create V3, replace step(12) set(myirf2)
irf graph irf, irf(V3) impulse(Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Depthchanges Liqpriceimpact)



*V2 PEPE/ETH
varsoc Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
var Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact, lags(1/3)
varstable
irf create PEPEV2, replace step(12) set(myirf)
irf graph irf, irf(PEPEV2) impulse(Orderimbalances AnnualizedSD Marketreturn) response(Depthchanges Liqpriceimpact)

*V3 PEPE/ETH
varsoc Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
var Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact, lags(1/3)
varstable
irf create PEPEV3, replace step(12) set(myirf2)
irf graph irf, irf(PEPEV3) impulse(Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Depthchanges Liqpriceimpact)






( 1,0,0,0,0 \ .,1,0,0,0 \ .,.,1,0,0 \ .,.,.,1,0 \ .,.,.,.,1 )
*SVAR1
*V2 ETH/USDC
var Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
matrix Aeq = ( 1,0,0,0,0 \ .,1,0,0,0 \ .,.,1,0,0 \ .,.,.,1,0 \ .,.,.,.,1 )

svar Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact, aeq(Aeq) lags(1/1)
irf create svar2_model, set(myirf1, replace)
irf graph oirf, response(Liqpriceimpact Depthchanges)
irf graph fevd, impulse(Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Liqpriceimpact Depthchanges)

*V3 ETH/USDC
var Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
matrix Aeq = ( 1,0,0,0,0 \ .,1,0,0,0 \ .,.,1,0,0 \ .,.,.,1,0 \ .,.,.,.,1 )

svar Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact, aeq(Aeq) lags(1/1)
irf create svar3_model, set(myirf2, replace)
irf graph oirf, response(Liqpriceimpact Depthchanges)
irf graph fevd, impulse(Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Liqpriceimpact Depthchanges)

*V2 PEPE/ETH
var Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
matrix Aeq = ( 1,0,0,0,0 \ .,1,0,0,0 \ .,.,1,0,0 \ .,.,.,1,0 \ .,.,.,.,1 )

svar Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact, aeq(Aeq) lags(1/3)
irf create svar4_model, set(myirf3, replace)
irf graph oirf, response(Liqpriceimpact Depthchanges)
irf graph fevd, impulse(Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Liqpriceimpact Depthchanges)


*V3 PEPE/ETH
var Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
matrix Aeq = ( 1,0,0,0,0 \ .,1,0,0,0 \ .,.,1,0,0 \ .,.,.,1,0 \ .,.,.,.,1 )

svar Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact, aeq(Aeq) lags(1/3)
irf create svar5_model, set(myirf4, replace)
irf graph oirf, response(Liqpriceimpact Depthchanges)
irf graph fevd, impulse(Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Liqpriceimpact Depthchanges)



*SVAR2
( 1,0,0,0,0 \ .,1,0,0,0 \ .,.,1,0,0 \ .,.,.,1,0 \ .,.,.,.,1 )
*V2 ETH/USDC
var AnnualizedSD Orderimbalances Marketreturn Depthchanges Liqpriceimpact
matrix Aeq = ( 1,0,0,0,0 \ .,1,0,0,0 \ .,.,1,0,0 \ .,.,.,1,0 \ .,.,.,.,1 )

svar AnnualizedSD Orderimbalances Marketreturn Depthchanges Liqpriceimpact, aeq(Aeq) lags(1/1)
irf create svar6_model, set(myirf5, replace)
irf graph oirf, response(Liqpriceimpact Depthchanges)
irf graph fevd, impulse(Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Liqpriceimpact Depthchanges)


*V3 ETH/USDC
var AnnualizedSD Orderimbalances Marketreturn Depthchanges Liqpriceimpact
matrix Aeq = ( 1,0,0,0,0 \ .,1,0,0,0 \ .,.,1,0,0 \ .,.,.,1,0 \ .,.,.,.,1 )

svar AnnualizedSD Orderimbalances Marketreturn Depthchanges Liqpriceimpact, aeq(Aeq) lags(1/1)
irf create svar7_model, set(myirf6, replace)
irf graph oirf, response(Liqpriceimpact Depthchanges)
irf graph fevd, impulse(Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Liqpriceimpact Depthchanges)


*V2 PEPE/ETH
var AnnualizedSD Orderimbalances Marketreturn Depthchanges Liqpriceimpact
matrix Aeq = ( 1,0,0,0,0 \ .,1,0,0,0 \ .,.,1,0,0 \ .,.,.,1,0 \ .,.,.,.,1 )

svar AnnualizedSD Orderimbalances Marketreturn Depthchanges Liqpriceimpact, aeq(Aeq) lags(1/3)
irf create svar8_model, set(myirf7, replace)
irf graph oirf, response(Liqpriceimpact Depthchanges)
irf graph fevd, impulse(Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Liqpriceimpact Depthchanges)


*V3 PEPE/ETH
var AnnualizedSD Orderimbalances Marketreturn Depthchanges Liqpriceimpact
matrix Aeq = ( 1,0,0,0,0 \ .,1,0,0,0 \ .,.,1,0,0 \ .,.,.,1,0 \ .,.,.,.,1 )

svar AnnualizedSD Orderimbalances Marketreturn Depthchanges Liqpriceimpact, aeq(Aeq) lags(1/3)
irf create svar9_model, set(myirf8, replace)
irf graph oirf, response(Liqpriceimpact Depthchanges)
irf graph fevd, impulse(Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Liqpriceimpact Depthchanges)





*SVAR3

matrix A = ( 1,0,0,0,0,0 .,1,0,0,0,0 \ .,.,1,0,0,0  \ .,.,.,1,0,0  \ .,.,.,.,1,0  \ .,.,.,.,.,1 )

*SVAR1
*V2 ETH/USDC
var Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
matrix Aeq = (1,0,0,0,0,0 \ .,1,0,0,0,0 \ .,.,1,0,0,0  \ .,.,.,1,0,0  \ .,.,.,.,1,0  \ .,.,.,.,.,1)

svar Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact, aeq(Aeq) lags(1/1)
irf create svar10_model, set(myirf9, replace)
irf graph oirf, response(Liqpriceimpact Depthchanges)
irf graph oirf, impulse(Gaschanges) response(Liqpriceimpact Depthchanges)
irf graph fevd, impulse(Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Liqpriceimpact Depthchanges)

*V3 ETH/USDC
var Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
matrix Aeq = (1,0,0,0,0,0 \ .,1,0,0,0,0 \ .,.,1,0,0,0  \ .,.,.,1,0,0  \ .,.,.,.,1,0  \ .,.,.,.,.,1)

svar Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact, aeq(Aeq) lags(1/1)
irf create svar11_model, set(myirf10, replace)
irf graph oirf, response(Liqpriceimpact Depthchanges)
irf graph oirf, impulse(Gaschanges) response(Liqpriceimpact Depthchanges)
irf graph fevd, impulse(Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Liqpriceimpact Depthchanges)

*V2 PEPE/ETH
var Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
matrix Aeq = (1,0,0,0,0,0 \ .,1,0,0,0,0 \ .,.,1,0,0,0  \ .,.,.,1,0,0  \ .,.,.,.,1,0  \ .,.,.,.,.,1)

svar Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact, aeq(Aeq) lags(1/3)
irf create svar12_model, set(myirf11, replace)
irf graph oirf, response(Liqpriceimpact Depthchanges)
irf graph oirf, impulse(Gaschanges) response(Liqpriceimpact Depthchanges)
irf graph fevd, impulse(Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Liqpriceimpact Depthchanges)


*V3 PEPE/ETH
var Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact
matrix Aeq = (1,0,0,0,0,0 \ .,1,0,0,0,0 \ .,.,1,0,0,0  \ .,.,.,1,0,0  \ .,.,.,.,1,0  \ .,.,.,.,.,1)

svar Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges Liqpriceimpact, aeq(Aeq) lags(1/3)
irf create svar13_model, set(myirf12, replace)
irf graph oirf, response(Liqpriceimpact Depthchanges)
irf graph oirf, impulse(Gaschanges) response(Liqpriceimpact Depthchanges)
irf graph fevd, impulse(Gaschanges Orderimbalances AnnualizedSD Marketreturn Depthchanges) response(Liqpriceimpact Depthchanges)






