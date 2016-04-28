import unittest

from src import wave

diff_for_gcov = '''
diff --git a/c/Dawei/tst/cases/alarm_parse_ut.cpp b/c/Dawei/tst/cases/alarm_parse_ut.cpp
index e9d143e..3fb5d8e 100644
--- a/c/Dawei/tst/cases/alarm_parse_ut.cpp
+++ b/c/Dawei/tst/cases/alarm_parse_ut.cpp
@@ -2,6 +2,8 @@
 #include "gmock/gmock.h"
 // Tests factorial of negative numbers.
 //
+#include <vector>
+using namespace std;
 using ::testing::_;
 using ::testing::SetArgPointee;
 using ::testing::DoAll;
@@ -9,6 +11,23 @@ using ::testing::Return;
 using ::testing::Pointee;
 
 extern int parse_afield(char *info, char *type, char *leng);
+extern int solve9_1_1(vector<int> array);
+
+TEST(sorted_group, test_one)
+{
+    int i;
+    vector<int> v;
+ 
+    for( i = 0; i < 10; i++ )
+    {
+        int ii = i * i + 2 * i;
+        v.push_back( ii );
+        printf("origin: %d, ", ii);
+    }
+    
+    int ret = solve9_1_1(v);
+    printf("\nsecond smaller: %d\n", ret);
+}
 
 void compose_info(char *info, char *alarm1, int size1, char *alarm2, int size2)
 {
'''

gcov_f = \
'''     -:    0:Source:../cases/alarm_parse_ut.cpp
        -:    0:Programs:4
        -:    1:#include "gtest/gtest.h"
        -:    2:#include "gmock/gmock.h"
        -:    3:// Tests factorial of negative numbers.
        -:    4://
        -:    5:#include <vector>
        -:    6:using namespace std;
        -:    7:using ::testing::_;
        -:    8:using ::testing::SetArgPointee;
        -:    9:using ::testing::DoAll;
        -:   10:using ::testing::Return;
        -:   11:using ::testing::Pointee;
        -:   12:
        -:   13:extern int parse_info_types(char *info, char *type, char *leng);
        -:   14:extern int solve9_1_1(vector<int> array);
        -:   15:
       20:   16:TEST(sorted_group, test_one)
        -:   17:{
        -:   18:    int i;
        4:   19:    vector<int> v;
        -:   20: 
       44:   21:    for( i = 0; i < 10; i++ )
        -:   22:    {
       40:   23:        int ii = i * i + 2 * i;
       40:   24:        v.push_back( ii );
       40:   25:        printf("origin: %d, ", ii);
        -:   26:    }
        -:   27:    
        4:   28:    int ret = solve9_1_1(v);
        4:   29:    printf("second smaller: %d", ret);
        4:   30:}
        -:   31:
        4:   32:void compose_info(char *info, char *alarm1, int size1, char *alarm2, int size2)
        -:   33:{
        4:   34:    memcpy(info, alarm1, size1);
        4:   35:    memcpy(&info[size1], alarm2, size2);
        4:   36:}
'''
expect_blocks = ['','']
expect_blocks[0] ='''
        -:    2:#include "gmock/gmock.h"
        -:    3:// Tests factorial of negative numbers.
        -:    4://
+       -:    5:#include <vector>
+       -:    6:using namespace std;
        -:    7:using ::testing::_;
        -:    8:using ::testing::SetArgPointee;
        -:    9:using ::testing::DoAll;
'''

expect_blocks[1] = '''
        -:   11:using ::testing::Pointee;
        -:   12:
        -:   13:extern int parse_info_types(char *info, char *type, char *leng);
+       -:   14:extern int solve9_1_1(vector<int> array);
+       -:   15:
+      20:   16:TEST(sorted_group, test_one)
+       -:   17:{
+       -:   18:    int i;
+       4:   19:    vector<int> v;
+       -:   20: 
+      44:   21:    for( i = 0; i < 10; i++ )
+       -:   22:    {
+      40:   23:        int ii = i * i + 2 * i;
+      40:   24:        v.push_back( ii );
+      40:   25:        printf("origin: %d, ", ii);
+       -:   26:    }
+       -:   27:    
+       4:   28:    int ret = solve9_1_1(v);
+       4:   29:    printf("second smaller: %d", ret);
        4:   30:}
        -:   31:
+       4:   32:void compose_info(char *info, char *alarm1, int size1, char *alarm2, int size2)
        -:   33:{
        4:   34:    memcpy(info, alarm1, size1);
        4:   35:    memcpy(&info[size1], alarm2, size2);
'''
class TestGcov(unittest.TestCase):
    def test_fetch_gcov(self):
        diffs =  wave.Diffs(diff_for_gcov)
        for _, patch in diffs.items():
            self._assert_gcov(wave.make_changed_gcov(patch, gcov_f))
            
    def _assert_gcov(self, gcov):
        block = gcov[0]
        self.assertTrue(block[0].strip().startswith('@@'))
        self._assert_block(expect_blocks[0], block[1:])
              
            
    def _assert_block(self, expect, block):
        for lines in block:
            self._assert_lines(expect, lines)

    def _assert_lines(self, expect, lines):
        self.assertListEqual(lines, expect.split('\n')[1:-1])
                