/**

给定两个字符串 s 和 t，长度分别是 m 和 n，返回 s 中的 最短窗口
子串，使得该子串包含 t
中的每一个字符（包括重复字符）。如果没有这样的子串，返回空字符串 ""。

测试用例保证答案唯一。

示例 1：

输入：s = "ADOBECODEBANC", t = "ABC"
输出："BANC"
解释：最小覆盖子串 "BANC" 包含来自字符串 t 的 'A'、'B' 和 'C'。
示例 2：

输入：s = "a", t = "a"
输出："a"
解释：整个字符串 s 是最小覆盖子串。
示例 3:

输入: s = "a", t = "aa"
输出: ""
解释: t 中两个字符 'a' 均应包含在 s 的子串中，
因此没有符合条件的子字符串，返回空字符串。

提示：

m == s.length
n == t.length
1 <= m, n <= 105
s 和 t 由英文字母组成

*/

#include <bench/competitive/problem.hpp>

#include <algorithm>
#include <deque>
#include <iterator>
#include <string>
#include <unordered_map>

using namespace std;

// class Solution {
//   public:
//     string minWindow(string s, string t) {
//         // char -> count
//         unordered_map<char, int> t_index;

//         // 1. init t's index
//         for (auto c : t) {
//             t_index[c]++;
//         }

//         string result;
//         auto t_index_copy = t_index;
//         auto i_changed = false;
//         string::iterator i;
//         auto next_i_changed = false;
//         string::iterator next_i;
//         // 2. iter s
//         for (auto c = s.begin(); c < s.end(); c++) {
//             if (t_index_copy.find(*c) != t_index_copy.end()) {
//                 if (!i_changed) {
//                     i = c;
//                     i_changed = true;
//                 }
//                 t_index_copy[*c]--;
//                 if (t_index_copy[*c] < 0 && !next_i_changed) {
//                     next_i = c;
//                     next_i_changed = true;
//                 }
//             }

//             // 2.1 judge t_index is below zero
//             bool is_all_bezero =
//                 all_of(t_index_copy.begin(), t_index_copy.end(),
//                        [](const pair<char, int>& x) { return x.second <= 0;
//                        });

//             // cout << t_index_copy << "," << is_all_bezero << endl;

//             if (is_all_bezero) {
//                 string substr(i, next(c));
//                 // cout << substr << endl;
//                 if (result.empty() || (substr.size() < result.size())) {
//                     result = substr;
//                 }
//                 t_index_copy = t_index;
//                 if (next_i_changed) {
//                     i = next_i;
//                     c = prev(next_i);
//                     next_i_changed = false;
//                     i_changed = true;
//                 } else {
//                     i_changed = false;
//                 }
//             }
//         }

//         return result;
//     }
// };

class Solution {
  public:
    string minWindow(string s, string t) {
        // char -> count
        unordered_map<char, int> t_index;

        // 1. init t's index
        for (auto c : t) {
            t_index[c]++;
        }

        string result;

        // 2. double pointer
        auto j = s.begin();
        size_t missing_ele = t_index.size();
        deque<string::iterator> nodes;
        while (j != s.end()) {
            // 2.1 扩大范围
            if (t_index.find(*j) != t_index.end()) {
                nodes.push_back(j);
                t_index[*j]--;
                if (t_index[*j] == 0) {
                    missing_ele--;
                }
            }

            if (missing_ele <= 0) {
                // 2.2 缩小范围
                while (t_index[*nodes.front()] < 0) {
                    t_index[*nodes.front()]++;
                    nodes.pop_front();
                }

                // 2.3 更新
                string substr(nodes.front(), next(j));
                if (result.empty() || (result.size() > substr.size())) {
                    result = substr;
                }

                // 2.4 已经到达当前范围最小子串，pop
                // 最前面，即改子串不需要再扩大了
                t_index[*nodes.front()]++;
                nodes.pop_front();
                missing_ele++;
            }

            j++;
        }

        return result;
    }
};

string sample1() {
    Solution sol;
    auto s = string("ADOBECODEBANC");
    auto t = string("ABC");
    return sol.minWindow(s, t);
}

string sample2() {
    Solution sol;
    auto s = string("a");
    auto t = string("a");
    return sol.minWindow(s, t);
}

string sample3() {
    Solution sol;
    auto s = string("a");
    auto t = string("aa");
    return sol.minWindow(s, t);
}

string sample4() {
    Solution sol;
    auto s = string("BDOAECODEBAAC");
    auto t = string("AABC");
    return sol.minWindow(s, t);
}

string sample5() {
    Solution sol;
    auto s = string("BDOAECODEAHKLBAGAC");
    auto t = string("AABC");
    return sol.minWindow(s, t);
}

string sample6() {
    Solution sol;
    auto s = string("bdab");
    auto t = string("ab");
    return sol.minWindow(s, t);
}

int answer() {
    cout << sample1() << "\n";
    cout << sample2() << "\n";
    cout << sample3() << "\n";
    cout << sample4() << "\n";
    cout << sample5() << "\n";
    cout << sample6() << "\n";
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)
