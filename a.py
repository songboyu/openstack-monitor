a = """Inode Number                  Inode File Path
---------------- ------------------ ---------
        34382705 0xffff88003aa67d98 /root/anaconda-ks.cfg
"""

b = """-rw-r--r-- 1 root root 6517 May  6 02:59 vol.py"""

print 'inode',a[109:127]
c = b.split()
print 'access',c[0]
print 'size',c[4]