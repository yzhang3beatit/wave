import unittest

from src import wave

diff_f = '''
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

 void compose_info(char *info, char *alarm1, int size1, char *alarm2, int size2)
 {

'''

class TestDiffs(unittest.TestCase):
    def test_diffs(self):
        diffs =  wave.Diffs(diff_f)
        expect_diffs = {'/c/Dawei/tst/cases/alarm_parse_ut.cpp':[['#include "gmock/gmock.h"', 5, 6]]}
        self.assertDictEqual(diffs, expect_diffs)


        