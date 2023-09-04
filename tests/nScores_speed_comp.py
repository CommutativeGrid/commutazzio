# from commutazzio.statistics import CL4_NIScores,CL4_NIScores_numba
# Is=[f"I{_}" for _ in range(1, 56)]
# Ns=[f"N{_}" for _ in range(1, 22)]
# Ls=Is+Ns
# mult_dict={k:random.randint(1, 100) for k in Ls}

# #  time the function, run for 1000 times

# import timeit
# start = timeit.default_timer()
# aaa=CL4_NIScores({k:random.randint(1, 100) for k in Ls})
# print(aaa.ns_const,aaa.ns_logistic(1))
# stop = timeit.default_timer()
# print('Time: ', stop - start)


# import timeit
# start = timeit.default_timer()
# bbb=CL4_NIScores_numba({k:random.randint(1, 100) for k in Ls})
# print(bbb.ns_const,bbb.ns_logistic(1))
# stop = timeit.default_timer()
# print('Time: ', stop - start)


# import timeit

# # Define the setup code
# setup_code = """
# from commutazzio.statistics import CL4_NIScores, CL4_NIScores_numba
# import random
# Ls = [f"I{_}" for _ in range(1, 56)] + [f"N{_}" for _ in range(1, 22)]
# """

# # Define the code for the first function
# code1 = """
# aaa=CL4_NIScores({k:random.randint(1, 100) for k in Ls})
# aaa.ns_const
# aaa.ns_logistic(1)
# aaa.ns_logistic(3)
# """

# # Define the code for the second function
# code2 = """
# bbb=CL4_NIScores_numba({k:random.randint(1, 100) for k in Ls})
# bbb.ns_const
# bbb.ns_logistic(1)
# bbb.ns_logistic(4)
# """

# # Time the execution of the first function
# time1 = timeit.timeit(setup=setup_code, stmt=code1, number=1000)
# print(f"Execution time for CL4_NIScores: {time1} seconds")

# # Time the execution of the second function
# time2 = timeit.timeit(setup=setup_code, stmt=code2, number=1000)
# print(f"Execution time for CL4_NIScores_numba: {time2} seconds")