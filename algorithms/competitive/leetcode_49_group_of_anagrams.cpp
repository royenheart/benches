/**

给你一个字符串数组，请你将 字母异位词 组合在一起。可以按任意顺序返回结果列表。

示例 1:

输入: strs = ["eat", "tea", "tan", "ate", "nat", "bat"]

输出: [["bat"],["nat","tan"],["ate","eat","tea"]]

解释：

在 strs 中没有字符串可以通过重新排列来形成 "bat"。
字符串 "nat" 和 "tan" 是字母异位词，因为它们可以重新排列以形成彼此。
字符串 "ate" ，"eat" 和 "tea" 是字母异位词，因为它们可以重新排列以形成彼此。
示例 2:

输入: strs = [""]

输出: [[""]]

示例 3:

输入: strs = ["a"]

输出: [["a"]]

提示：

1 <= strs.length <= 104
0 <= strs[i].length <= 100
strs[i] 仅包含小写字母

*/

#include <bench/competitive/problem.hpp>

#include <algorithm>
#include <array>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

struct ArrayHash {
    size_t operator()(const array<int, 26>& arr) const {
        size_t h = 0;
        for (int x : arr) {
            h = h * 131 + x;
        }
        return h;
    }
};

class Solution {
  public:
    vector<vector<string>> groupAnagrams(vector<string>& strs) {
        vector<vector<string>> results = {};
        for (auto str : strs) {
            int length = str.length();
            array<int, 26> hash{};
            for (auto c : str) {
                hash[c - 'a']++;
            }
            if (bucket[length].count(hash) > 0) {
                results[bucket[length][hash]].push_back(str);
            } else {
                vector<string> new_vec = {str};
                auto len = results.size();
                results.push_back(new_vec);
                bucket[length][hash] = len;
            }
        }
        return results;
    }

  private:
    unordered_map<array<int, 26>, size_t, ArrayHash> bucket[101];
};

vector<vector<string>> sample1() {
    Solution sol;
    auto q1 = vector({string("ab"), string("ba"), string("ccc"), string("ac")});
    return sol.groupAnagrams(q1);
}

int answer() {
    cout << sample1() << endl;
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)
