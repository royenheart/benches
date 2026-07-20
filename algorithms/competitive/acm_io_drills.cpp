// ACM 模式 cin/cout 输入输出训练
//
// 本文件不解决单一题目，而是一个 I/O "实训 workbook"。
// 顶部 answer() 会先读取一个 drill 编号 k，然后分发到对应的
// drill_k() 函数去处理该编号所对应的输入形状。
// 每个 drill 集中演示一种在 ACM/OJ 题目中非常常见、但容易卡壳的
// 输入处理手法，并在注释中标注了关键易错点。
//
// 通过 BENCH_IO_TEST 提供的多个用例可逐个跑通验证，命令：
//   xmake build algo_acm_io_drills_test
//   xmake run   algo_acm_io_drills_test
//
// 各 drill 覆盖的常见 I/O 形态：
//   1  T 组查询（计数前缀）
//   2  读到 EOF（while (cin >> x)）
//   3  哨兵终止（读到 "0 0" 停）
//   4  整数 + 含空格的字符串行（getline 与 >> 混用）
//   5  字符矩阵（无空格，逐行 cin >>）
//   6  字符矩阵（含空格，必须逐行 getline）
//   7  图输入：n 结点 m 边，随后 m 行 u v w
//   8  多组数据，每组是 n*m 矩阵求和（用例嵌套）
//   9  每行不定数量的整数（getline + istringstream）
//   10 输出格式：末尾无空格 + 固定小数位
//   11 箭头分隔的多条链表："1->2->3, 3->4->5"（分隔符替换 + istringstream）
//
// 各 drill 注释里的输入示例均省略首行的 drill 编号 k，
// 展示的是 dispatch 读掉 k 之后、对应 drill 函数实际读到的输入。

#include <bench/competitive/problem.hpp>

#include <iomanip>
// input / output stream
#include <iostream>
// string stream
#include <sstream>
#include <string>
#include <vector>

// Drill 1: 计数前缀 T，随后 T 个整数求和。
// 输入示例：
//   3
//   1 2 3
// 输出：6
// 易错点：忘记 while (T--) 循环读 T 个，直接读一行就当结果。
int drill_count_prefix() {
    int T;
    if (!(std::cin >> T)) {
        return 0;
    }
    long long total = 0;
    while (T--) {
        int x;
        std::cin >> x;
        total += x;
    }
    std::cout << total << '\n';
    return 0;
}

// Drill 2: 一直读到 EOF，累加所有整数。
// 输入示例：
//   5 5 5
// 输出：15
// 易错点：不确定输入条目数量时不能用计数循环，必须用
//   while (std::cin >> x) 它会在 EOF 或输入耗尽时自然退出。
int drill_read_until_eof() {
    long long total = 0;
    int x;
    while (std::cin >> x) {
        total += x;
    }
    std::cout << total << '\n';
    return 0;
}

// Drill 3: 每次两个整数 a b，遇到哨兵 "0 0" 即停止。
// 输入示例：
//   1 2
//   3 4
//   0 0
// 输出：10
// 易错点：哨兵判定须放在累加之前，否则会把哨兵本身也算进去。
int drill_sentinel() {
    long long total = 0;
    int a, b;
    while (std::cin >> a >> b) {
        if (a == 0 && b == 0) {
            break;
        }
        total += a + b;
    }
    std::cout << total << '\n';
    return 0;
}

// Drill 4: 整数 n 后接 n 行字符串（可能含空格）。
// 输入示例：
//   2
//   hello world
//   foo bar baz
// 输出：
//   2
//   11:hello world
//   11:foo bar baz
// 易错点（ACM 最大的坑之一）：cin >> n 之后换行符会残留在缓冲区，
// 直接 getline 会读到空行。要么用 std::cin >> std::ws 跳过空白，
// 要么显式 getline 一次将其吃掉。这里用 std::ws。
// 1. getlines: 只要遇到 '\n' 换行符即表示读取结束
// 2. cin >>，cin 不会每次都要从文件读取，而是会有一个缓冲区，提高性能。但是 cin
// 遇到空格、'\n' 等间隔符号停止。
int drill_mixed_int_strings() {
    int n;
    std::cin >> n;
    std::cin >> std::ws; // 关键：吞掉 >> 留下的换行
    std::vector<std::string> lines;
    lines.reserve(static_cast<std::size_t>(n));
    for (int i = 0; i < n; ++i) {
        std::string s;
        std::getline(std::cin, s);
        lines.push_back(s);
    }
    std::cout << lines.size() << '\n';
    for (const auto& s : lines) {
        std::cout << s.size() << ':' << s << '\n';
    }
    return 0;
}

// Drill 5: n 行 m 列、字符不含空格的字符矩阵。
// 输入示例：
//   2 3
//   ###
//   .#.
// 输出：4
// 易错点：误以为字符矩阵必须按字符读，实际上没有空格时
//   std::cin >> row（row 是 std::string）会自动按空白分隔读取一行。
int drill_char_grid() {
    int n, m;
    std::cin >> n >> m;
    std::vector<std::string> grid;
    grid.reserve(static_cast<std::size_t>(n));
    for (int i = 0; i < n; ++i) {
        std::string row;
        std::cin >> row;
        grid.push_back(row);
    }
    int walls = 0;
    for (const auto& row : grid) {
        for (char c : row) {
            if (c == '#') {
                ++walls;
            }
        }
    }
    std::cout << walls << '\n';
    return 0;
}

// Drill 6: n 行字符矩阵，但行内含空格（必须是合法字符）。
// 输入示例：
//   2
//   # #
//   .#.#
// 输出：4
// 易错点：>> 遇到空格会切分，无法得到原来的行；必须 getline。
// 又因为前面有计数读取 n，仍需要 std::ws 清理缓冲区。
int drill_char_grid_spaces() {
    int n;
    std::cin >> n >> std::ws;
    int walls = 0;
    for (int i = 0; i < n; ++i) {
        std::string row;
        std::getline(std::cin, row);
        for (char c : row) {
            if (c == '#') {
                ++walls;
            }
        }
    }
    std::cout << walls << '\n';
    return 0;
}

// Drill 7: 图输入：首行 n m，随后 m 行 "u v w"，输出总权重。
// 输入示例：
//   3 3
//   1 2 5
//   2 3 10
//   1 3 7
// 输出：22
// 易错点：忽略 n 这个上下文，只用 m 循环读边；但很多题目先给节点数
//   再给边数，读完两个数后才进入边循环。两者 cout 出来后顺序要稳。
int drill_graph() {
    int n, m;
    std::cin >> n >> m;
    long long total = 0;
    for (int i = 0; i < m; ++i) {
        int u, v, w;
        std::cin >> u >> v >> w;
        total += w;
    }
    std::cout << total << '\n';
    return 0;
}

// Drill 8: 多组数据。首行 T = 用例数；每个用例首行 n m，然后 n*m 个数
// 输出每个用例的矩阵和，使用 endl 之外的 '\n' 以达到流式刷新。
// 输入示例：
//   2
//   2 2
//   1 2 3 4
//   3 3
//   1 2 3 4 5 6 7 8 9
// 输出：
//   10
//   45
// 易错点：多组容易把外层 T 与用例内部的 n 混为一谈；必须分层。
int drill_multitest_matrix() {
    int T;
    std::cin >> T;
    while (T--) {
        int n, m;
        std::cin >> n >> m;
        long long sum = 0;
        const int cells = n * m;
        for (int i = 0; i < cells; ++i) {
            int x;
            std::cin >> x;
            sum += x;
        }
        std::cout << sum << '\n';
    }
    return 0;
}

// Drill 9: 每行不定数量的整数（行长度不一）。
// 用 getline 把整行接住，再用 istringstream 重新解析。
// 输入示例：
//   3
//   1 2 3
//   4 5
//   6
// 输出：6,9,6
// 易错点：直接 >> 读取时无法知道每行止于何处——必须按行读再二次解析。
int drill_line_stream() {
    int n;
    std::cin >> n >> std::ws;
    std::vector<long long> sums;
    sums.reserve(static_cast<std::size_t>(n));
    for (int i = 0; i < n; ++i) {
        std::string line;
        std::getline(std::cin, line);
        std::istringstream iss(line);
        long long s = 0;
        int x;
        while (iss >> x) {
            s += x;
        }
        sums.push_back(s);
    }
    for (std::size_t i = 0; i < sums.size(); ++i) {
        if (i) {
            std::cout << ',';
        }
        std::cout << sums[i];
    }
    std::cout << '\n';
    return 0;
}

// Drill 10: 输出格式训练：行内空格分隔（末尾不允许有空格），
// 且最后的总和输出保留两位小数。
// 输入示例：
//   3
//   1.5 2.5 3.0
// 输出：
//   1.5 2.5 3
//   7.00
// 易错点：① 末尾空格用朴素 "cout << x << ' '" 会在行尾多空格；
//   ② 忘了先存 std::cout 的格式 flag，后面想恢复默认输出会出错。
int drill_output_format() {
    int n;
    std::cin >> n;
    std::vector<double> v;
    v.reserve(static_cast<std::size_t>(n));
    for (int i = 0; i < n; ++i) {
        double x;
        std::cin >> x;
        v.push_back(x);
    }
    for (int i = 0; i < n; ++i) {
        if (i) {
            std::cout << ' ';
        }
        std::cout << v[static_cast<std::size_t>(i)];
    }
    std::cout << '\n';
    double total = 0;
    for (double x : v) {
        total += x;
    }
    // 保存并复用旧的格式状态，避免后续输出受 fixed 污染
    std::ios_base::fmtflags old_flags = std::cout.flags();
    std::streamsize old_prec = std::cout.precision();
    std::cout << std::fixed << std::setprecision(2) << total << '\n';
    std::cout.flags(old_flags);
    std::cout.precision(old_prec);
    return 0;
}

// Drill 11 专用：单链表节点，与仓库 leetcode 题文件中的定义保持一致。
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    explicit ListNode(int x) : val(x), next(nullptr) {}
};

// 把 "1->2->3" 这样的一段解析成整数序列。
// 技巧：多字符分隔符 "->" 先整体替换成空格，再交给 istringstream 按空白
// 读 int；负数（如 "1->-2"）也因此能被正确解析。
std::vector<int> parse_arrow_values(std::string segment) {
    // 查找 -> 位置，然后从这个位置开始把两个字符替换为空格
    for (std::size_t pos = 0;
         (pos = segment.find("->", pos)) != std::string::npos;) {
        segment.replace(pos, 2, " ");
    }
    std::vector<int> values;
    std::istringstream iss(segment);
    int x;
    while (iss >> x) {
        values.push_back(x);
    }
    return values;
}

// 把链表按 "a->b->c" 形式重新打印，同时验证解析与建链都正确。
void print_arrow_list(const ListNode* head) {
    for (const ListNode* cur = head; cur != nullptr; cur = cur->next) {
        if (cur != head) {
            std::cout << "->";
        }
        std::cout << cur->val;
    }
    std::cout << '\n';
}

// Drill 11: 一行多条箭头分隔的链表："1->2->3, 3->4->5"（逗号后可带空格）。
// 输入示例：
//   1->2->3, 3->4->5
// 输出：
//   1->2->3
//   3->4->5
// 手法：先按 ',' 切段，每段经 parse_arrow_values 得到整数序列后建链。
// 易错点：① "->" 是多字符分隔符，iss >> int 无法直接跳过它（读到 '-'
//   后紧跟 '>' 会解析失败），必须先替换分隔符或手写 find 循环切 token；
//   ② 逗号两侧的空白无需手写 trim，istringstream 的 >> 会自动跳过；
//   ③ dispatch 里的 >> k 会残留换行，getline 之前仍需 std::ws。
// 节点内存用 bench::competitive::make_singly_list 托管；裸 OJ 提交时
// 换成 new ListNode(x) 逐个挂载即可（进程退出时统一回收）。
int drill_arrow_linked_lists() {
    std::string line;
    if (!std::getline(std::cin >> std::ws, line)) {
        return 0;
    }
    std::size_t begin = 0;
    while (true) {
        const std::size_t comma = line.find(',', begin);
        auto list = bench::competitive::make_singly_list<ListNode>(
            parse_arrow_values(line.substr(begin, comma - begin)));
        print_arrow_list(list.head());
        if (comma == std::string::npos) {
            break;
        }
        begin = comma + 1;
    }
    return 0;
}

// 顶层分发：先读 drill 编号 k，按 k 调用对应的 drill。
// 这种"先选编号再跑对应逻辑"的写法本身也模拟了多组数据中
// "首行 select case" 的常见模式。
int answer() {
    int k;
    if (!(std::cin >> k)) {
        return 0;
    }
    switch (k) {
    case 1:
        return drill_count_prefix();
    case 2:
        return drill_read_until_eof();
    case 3:
        return drill_sentinel();
    case 4:
        return drill_mixed_int_strings();
    case 5:
        return drill_char_grid();
    case 6:
        return drill_char_grid_spaces();
    case 7:
        return drill_graph();
    case 8:
        return drill_multitest_matrix();
    case 9:
        return drill_line_stream();
    case 10:
        return drill_output_format();
    case 11:
        return drill_arrow_linked_lists();
    default:
        return 1;
    }
}

BENCH_COMPETITIVE_MAIN(answer)

// ---- 各 drill 的 IO 用例 ----
// 输入首行均为 drill 编号 k，dispatch 后再交给对应函数处理剩余输入。

BENCH_IO_TEST("drill 1: 计数前缀 T 个求和", "1\n3\n1 2 3\n", "6\n", 0, answer)

BENCH_IO_TEST("drill 2: 读到 EOF 累加", "2\n5 5 5\n", "15\n", 0, answer)

BENCH_IO_TEST("drill 3: 哨兵 0 0 终止", "3\n1 2\n3 4\n0 0\n", "10\n", 0, answer)

BENCH_IO_TEST("drill 4: 整数 + 含空格字符串行",
              "4\n2\nhello world\nfoo bar baz\n",
              "2\n11:hello world\n11:foo bar baz\n", 0, answer)

BENCH_IO_TEST("drill 5: 字符矩阵（无空格）", "5\n2 3\n###\n.#.\n", "4\n", 0,
              answer)

BENCH_IO_TEST("drill 6: 字符矩阵（含空格，getline）", "6\n2\n# #\n.#.#\n",
              "4\n", 0, answer)

BENCH_IO_TEST("drill 7: 图输入 n m + m 条边", "7\n3 3\n1 2 5\n2 3 10\n1 3 7\n",
              "22\n", 0, answer)

BENCH_IO_TEST("drill 8: 多组测试，每组 n*m 矩阵和",
              "8\n2\n2 2\n1 2 3 4\n3 3\n1 2 3 4 5 6 7 8 9\n", "10\n45\n", 0,
              answer)

BENCH_IO_TEST("drill 9: 每行不定长整数和（istringstream）",
              "9\n3\n1 2 3\n4 5\n6\n", "6,9,6\n", 0, answer)

BENCH_IO_TEST("drill 10: 末尾无空格 + 两位小数", "10\n3\n1.5 2.5 3.0\n",
              "1.5 2.5 3\n7.00\n", 0, answer)

BENCH_IO_TEST("drill 11: 箭头分隔的两条链表", "11\n1->2->3, 3->4->5\n",
              "1->2->3\n3->4->5\n", 0, answer)

BENCH_IO_TEST("drill 11: 逗号后带空格 + 负数节点", "11\n10->-3, 7->8->9\n",
              "10->-3\n7->8->9\n", 0, answer)

// perf 框架会把同一份 input 每次迭代重新灌入 std::cin
// 跑一次，所以字面量必须是单次合法 dispatch。
BENCH_PERF_TEST("drill 7 解析 100 节点 64 条边", answer,
                "7\n100 64\n"
                "1 2 1\n1 3 2\n1 4 3\n1 5 4\n1 6 5\n1 7 6\n1 8 7\n1 9 8\n"
                "2 3 1\n2 4 2\n2 5 3\n2 6 4\n2 7 5\n2 8 6\n2 9 7\n2 10 8\n"
                "3 4 1\n3 5 2\n3 6 3\n3 7 4\n3 8 5\n3 9 6\n3 10 7\n4 10 8\n"
                "4 5 1\n4 6 2\n4 7 3\n4 8 4\n4 9 5\n5 6 1\n5 7 2\n5 8 3\n"
                "6 7 1\n6 8 2\n6 9 3\n6 10 4\n"
                "7 8 1\n7 9 2\n7 10 3\n"
                "8 9 1\n8 10 2\n9 10 1\n"
                "1 10 1\n2 9 2\n3 8 3\n4 9 4\n"
                "5 10 1\n6 9 2\n7 10 3\n"
                "10 1 1\n9 1 2\n8 1 3\n7 1 4\n"
                "6 1 1\n5 1 2\n4 1 3\n3 1 4\n"
                "2 1 1\n1 2 2\n10 5 3\n9 6 4\n"
                "8 7 1\n7 6 2\n6 5 3\n5 4 4\n"
                "4 3 1\n3 2 2\n1 8 1\n2 7 2\n",
                1000)
