import glob
def retrieve_filename(old,new):
    puv_list_old=glob.glob(old+'S2*_T48PUV_*.TIF')
    pvv_list_old=glob.glob(old+'S2*_T48PVV_*.TIF')
    puv_list_new=glob.glob(new+'S2*_T48PUV_*.TIF')
    pvv_list_new=glob.glob(new+'S2*_T48PVV_*.TIF')
    return(puv_list_old,pvv_list_old,puv_list_new,pvv_list_new)
