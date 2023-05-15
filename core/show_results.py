from calculate import runCalculations
from timeit import default_timer as timer

start_time = timer()

# static inputs
modulusE = 200000
yield_mpa = 300
phi = 0.9
Kx = 1
Ky = 1

steel_class = "class C"
stress_factor = 1.34
if steel_class == "class H":
    stress_factor = 2.24

### OUTPUTS
## show intermediate calculation steps
def showSteps(result, target, ratio_Kx, ratio_Ky, lambda_K, Lx, Ly, radius_gx, radius_gy, area, Cr):
    if target == "Cr":
        kRatio_formula = "Kx*Lx/rx and Ky*Ly/ry < 200"
        kxRatio_num = "Kx Ratio: " + str(Kx)+"*"+str(round(Lx*1000, 2))+"mm/"+str(radius_gx)+"mm = "+str(ratio_Kx)
        kyRatio_num = "Ky Ratio: " + str(Ky)+"*"+str(round(Ly*1000, 2))+"mm/"+str(radius_gy)+"mm = "+str(ratio_Ky)

        lambdaK_formula = "lambda = KL/r*sqrt(Fy/(E*pi^2))"
        lambdaK_num = str(max(ratio_Kx, ratio_Ky))+"*"\
            +"sqrt("+str(yield_mpa)+"/"+"("+str(modulusE)+"pi^2)) = "+str(lambda_K)
        
        Cr_formula = "Cr = phi*Fy*A*(1 + lambda^(2*1.34))^(-1/1.34)"
        Cr_num = str(phi)+"*"+str(yield_mpa)+"MPa*"+str(area)+"mm^2*(1 + "+str(lambda_K)+"^2.68)^(-1/1.34) = "+str(result)+" kN"
        
        return kRatio_formula, kxRatio_num, kyRatio_num, lambdaK_formula, lambdaK_num, Cr_formula, Cr_num      
    else:
        lambda_formula = "lambda = ([Cr/(phi*Fy*A)]^(-1.34) - 1)^(1/2.68)"
        lambda_num = "(["+str(Cr)+str(phi)+"*"+str(area)+"*"+str(yield_mpa)+"]^(-1.34) - 1)^(1/2.68) = "+str(result)

        kRatio_formula = "L = [lambda/sqrt(Fy/(E*pi^2))]*r/K"
        kRatio_num = "Maximum unbraced length (Ly) = "+str(round(result, 2))+" mm"

        return lambda_formula, lambda_num, kRatio_formula, kRatio_num

## printing outputs
def formatCalculations(result, target, ratio_Kx, ratio_Ky, lambda_K, Lx, Ly, radius_gx, radius_gy, area, Cr):
    # base case
    if target == "Cr":
        kRatio_formula, kxRatio_num, kyRatio_num, lambdaK_formula, lambdaK_num, Cr_formula, Cr_num = \
        showSteps(result, target, ratio_Kx, ratio_Ky, lambda_K, Lx, Ly, radius_gx, radius_gy, area, Cr)

        print("\n", kRatio_formula, "\n", kxRatio_num, "\n", kyRatio_num, "\n\n", lambdaK_formula, "\n", lambdaK_num, "\n\n", Cr_formula, "\n", Cr_num)
    # back calculate
    elif target != "Cr":
        lambda_formula, lambda_num, kRatio_formula, kRatio_num = showSteps(result, target, ratio_Kx, ratio_Ky, lambda_K, Lx, Ly, radius_gx, radius_gy, area, Cr)
        print("\n", lambda_formula, "\n", lambda_num, "\n\n", kRatio_formula, "\n", kRatio_num)

def printOutputs(question):
    result, target, ratio_Kx, ratio_Ky, lambda_K, Lx, Ly, radius_gx, radius_gy, area, Cr = runCalculations(question)

    formatCalculations(result, target, ratio_Kx, ratio_Ky, lambda_K, Lx, Ly, radius_gx, radius_gy, area, Cr)

# question = "Given a W360x33 column with a length of 7.0 meters braced twice at the y axis at 8.2ft and 5000mm, calculate Cr"
# printOutputs(question)

end_time = timer()
print("\n", end_time - start_time)  