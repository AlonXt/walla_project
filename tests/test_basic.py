def items(**kwargs):
    print(kwargs)
    return kwargs
    
    
kwargs = items(a=1,b=2,c=3)
print(type(kwargs))