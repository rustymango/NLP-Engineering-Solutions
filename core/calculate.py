import math

# calculations
def calculate(yield_mpa, modulusE, steel_class, phi, area):
    ratio_Kx = 0
    ratio_Ky = 0

    if ratio_Kx > ratio_Ky:
        lambda_K = ratio_Kx*math.sqrt(yield_mpa/(modulusE*math.pi**2))
    else:
        lambda_K = ratio_Ky*math.sqrt(yield_mpa/(modulusE*math.pi)**2)

    stress_factor = 1.34
    if steel_class == "class H":
        stress_factor = 2.24

    # show intermediate steps to calculate

    # answer
    compressiveR = phi*area*yield_mpa*(1 + lambda_K**(2*stress_factor))**(-1/stress_factor)

    answer = []

    return answer