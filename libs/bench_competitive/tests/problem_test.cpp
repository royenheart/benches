#include <bench/competitive/problem.hpp>
#include <gtest/gtest.h>

#include <cstddef>
#include <deque>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

struct CompetitiveTestListNode {
    int val;
    CompetitiveTestListNode* next;

    CompetitiveTestListNode() : val(0), next(nullptr) {}
    explicit CompetitiveTestListNode(int x) : val(x), next(nullptr) {}
};

struct CompetitiveTestDoublyListNode {
    int val;
    CompetitiveTestDoublyListNode* next;
    CompetitiveTestDoublyListNode* prev;

    CompetitiveTestDoublyListNode() : val(0), next(nullptr), prev(nullptr) {}
    explicit CompetitiveTestDoublyListNode(int x)
        : val(x), next(nullptr), prev(nullptr) {}
};

struct CompetitiveTestTreeNode {
    int val;
    CompetitiveTestTreeNode* left;
    CompetitiveTestTreeNode* right;

    explicit CompetitiveTestTreeNode(int x)
        : val(x), left(nullptr), right(nullptr) {}
    CompetitiveTestTreeNode(int x, CompetitiveTestTreeNode* left_node,
                            CompetitiveTestTreeNode* right_node)
        : val(x), left(left_node), right(right_node) {}
};

struct CompetitiveCustomTreeNode {
    int data;
    CompetitiveCustomTreeNode* lchild;
    CompetitiveCustomTreeNode* rchild;

    explicit CompetitiveCustomTreeNode(int x)
        : data(x), lchild(nullptr), rchild(nullptr) {}
};

namespace bench::competitive {

template <> struct binary_tree_node_traits<CompetitiveCustomTreeNode> {
    static int& value(CompetitiveCustomTreeNode& node) { return node.data; }
    static CompetitiveCustomTreeNode*& left(CompetitiveCustomTreeNode& node) {
        return node.lchild;
    }
    static CompetitiveCustomTreeNode*& right(CompetitiveCustomTreeNode& node) {
        return node.rchild;
    }
};

} // namespace bench::competitive

namespace {

int increment_answer() {
    int value = 0;
    std::cin >> value;
    std::cout << value + 1;
    return 7;
}

int quiet_answer() {
    int value = 0;
    std::cin >> value;
    return value;
}

} // namespace

TEST(CompetitiveProblem, RunIoCaseCapturesOutputAndReturnValue) {
    const auto result = bench::competitive::run_io_case("increment", "41", "42",
                                                        7, increment_answer);

    EXPECT_EQ(result.name, "increment");
    EXPECT_EQ(result.actual_return, 7);
    EXPECT_EQ(result.expected_return, 7);
    EXPECT_EQ(result.actual_output, "42");
    EXPECT_EQ(result.expected_output, "42");
    EXPECT_TRUE(result.passed());
}

TEST(CompetitiveProblem, RunValueCaseComparesExpressionResult) {
    const auto result =
        bench::competitive::run_value_case("value", [] { return 21 * 2; }, 42);

    EXPECT_EQ(result.name, "value");
    EXPECT_EQ(result.actual_value, 42);
    EXPECT_EQ(result.expected_value, 42);
    EXPECT_TRUE(result.passed());
}

TEST(CompetitiveProblem, PrintsVectorForDebugging) {
    std::ostringstream output;
    output << std::vector<int>{1, 2, 3};

    EXPECT_EQ(output.str(), "[1, 2, 3]");
}

TEST(CompetitiveProblem, PrintsNestedQueueCandidatesForDebugging) {
    std::ostringstream output;
    output << std::deque<std::tuple<int, int>>{{3, 1}, {-1, 2}};

    EXPECT_EQ(output.str(), "[(3, 1), (-1, 2)]");
}

TEST(CompetitiveProblem, BuildsSinglyLinkedListFromInitializerList) {
    auto list = bench::competitive::make_singly_list<CompetitiveTestListNode>(
        {1, 2, 3});

    ASSERT_NE(list.head(), nullptr);
    EXPECT_EQ(list.to_vector(), (std::vector<int>{1, 2, 3}));
    EXPECT_EQ(list.node_at(0)->next, list.node_at(1));
    EXPECT_EQ(list.node_at(1)->next, list.node_at(2));
    EXPECT_EQ(list.node_at(2)->next, nullptr);
}

TEST(CompetitiveProblem, ConvertsRewiredSinglyLinkedListToVector) {
    auto list = bench::competitive::make_singly_list<CompetitiveTestListNode>(
        {1, 2, 3});

    auto* first = list.node_at(0);
    auto* second = list.node_at(1);
    first->next = second->next;
    second->next = first;

    EXPECT_EQ(list.to_vector(second), (std::vector<int>{2, 1, 3}));
}

TEST(CompetitiveProblem, BuildsEmptySinglyLinkedList) {
    auto list =
        bench::competitive::make_singly_list<CompetitiveTestListNode>({});

    EXPECT_EQ(list.head(), nullptr);
    EXPECT_TRUE(list.to_vector().empty());
}

TEST(CompetitiveProblem, ConvertsMergedLinkedListsWithFreeFunction) {
    auto list1 = bench::competitive::make_singly_list<CompetitiveTestListNode>(
        {1, 4, 5});
    auto list2 = bench::competitive::make_singly_list<CompetitiveTestListNode>(
        {1, 3, 4});
    auto list3 =
        bench::competitive::make_singly_list<CompetitiveTestListNode>({2, 6});

    list1.node_at(0)->next = list2.node_at(0);
    list2.node_at(0)->next = list3.node_at(0);
    list3.node_at(0)->next = list2.node_at(1);

    const auto total_size = list1.size() + list2.size() + list3.size();

    EXPECT_EQ(
        bench::competitive::linked_list_to_vector(list1.head(), total_size),
        (std::vector<int>{1, 1, 2, 3, 4}));
}

TEST(CompetitiveProblem, BuildsDoublyLinkedListFromInitializerList) {
    auto list =
        bench::competitive::make_doubly_list<CompetitiveTestDoublyListNode>(
            {1, 2, 3});

    ASSERT_NE(list.head(), nullptr);
    EXPECT_EQ(list.to_vector(), (std::vector<int>{1, 2, 3}));
    EXPECT_EQ(list.node_at(0)->prev, nullptr);
    EXPECT_EQ(list.node_at(1)->prev, list.node_at(0));
    EXPECT_EQ(list.node_at(2)->prev, list.node_at(1));
    EXPECT_EQ(list.node_at(2)->next, nullptr);
}

TEST(CompetitiveProblem, SerializesBinaryTreeToLeetCodeLevelStrings) {
    CompetitiveTestTreeNode node9(9);
    CompetitiveTestTreeNode node15(15);
    CompetitiveTestTreeNode node7(7);
    CompetitiveTestTreeNode node20(20, &node15, &node7);
    CompetitiveTestTreeNode root(3, &node9, &node20);

    EXPECT_EQ(
        bench::competitive::binary_tree_to_level_strings(&root, 5),
        (std::vector<std::string>{"3", "9", "20", "null", "null", "15", "7"}));
}

TEST(CompetitiveProblem, TrimsTrailingNullsWhenSerializingBinaryTree) {
    CompetitiveTestTreeNode node2(2);
    CompetitiveTestTreeNode root(1, nullptr, &node2);

    EXPECT_EQ(bench::competitive::binary_tree_to_level_strings(&root, 2),
              (std::vector<std::string>{"1", "null", "2"}));
}

TEST(CompetitiveProblem, PrettyPrintsBinaryTreeForDebugging) {
    CompetitiveTestTreeNode node9(9);
    CompetitiveTestTreeNode node15(15);
    CompetitiveTestTreeNode node7(7);
    CompetitiveTestTreeNode node20(20, &node15, &node7);
    CompetitiveTestTreeNode root(3, &node9, &node20);

    EXPECT_EQ(bench::competitive::binary_tree_pretty(&root, 5),
              "3\n"
              "|-- L: 9\n"
              "`-- R: 20\n"
              "    |-- L: 15\n"
              "    `-- R: 7");
}

TEST(CompetitiveProblem, SupportsCustomBinaryTreeTraits) {
    CompetitiveCustomTreeNode left(4);
    CompetitiveCustomTreeNode right(5);
    CompetitiveCustomTreeNode root(8);
    root.lchild = &left;
    root.rchild = &right;

    EXPECT_EQ(bench::competitive::binary_tree_to_level_strings(&root, 3),
              (std::vector<std::string>{"8", "4", "5"}));
}

TEST(CompetitiveProblem, BuildsBinaryTreeFromDenseLevelValues) {
    auto tree = bench::competitive::make_binary_tree<CompetitiveTestTreeNode>(
        {1, 2, 3});

    ASSERT_NE(tree.root(), nullptr);
    EXPECT_EQ(tree.size(), std::size_t{3});
    EXPECT_EQ(tree.node_at(0), tree.root());
    EXPECT_EQ(tree.root()->left, tree.node_at(1));
    EXPECT_EQ(tree.root()->right, tree.node_at(2));
    EXPECT_EQ(tree.to_level_strings(),
              (std::vector<std::string>{"1", "2", "3"}));
}

TEST(CompetitiveProblem, BuildsBinaryTreeFromLeetCodeLevelValuesWithNulls) {
    using OptionalInt = std::optional<int>;

    auto tree = bench::competitive::make_binary_tree<CompetitiveTestTreeNode>(
        {OptionalInt{1}, std::nullopt, OptionalInt{2}, OptionalInt{3}});

    ASSERT_NE(tree.root(), nullptr);
    EXPECT_EQ(tree.size(), std::size_t{3});
    EXPECT_EQ(tree.root()->left, nullptr);
    EXPECT_EQ(tree.root()->right, tree.node_at(2));
    EXPECT_EQ(tree.node_at(2)->left, tree.node_at(3));
    EXPECT_EQ(tree.to_level_strings(),
              (std::vector<std::string>{"1", "null", "2", "3"}));
}

TEST(CompetitiveProblem, BuildsEmptyBinaryTree) {
    using OptionalInt = std::optional<int>;

    auto tree = bench::competitive::make_binary_tree<CompetitiveTestTreeNode>(
        std::initializer_list<OptionalInt>{});

    EXPECT_EQ(tree.root(), nullptr);
    EXPECT_EQ(tree.size(), std::size_t{0});
    EXPECT_TRUE(tree.to_level_strings().empty());
    EXPECT_EQ(tree.pretty(), "null");
}

TEST(CompetitiveProblem, BuildsBinaryTreeWithCustomTraits) {
    auto tree = bench::competitive::make_binary_tree<CompetitiveCustomTreeNode>(
        {8, 4, 5});

    ASSERT_NE(tree.root(), nullptr);
    EXPECT_EQ(tree.root()->lchild, tree.node_at(1));
    EXPECT_EQ(tree.root()->rchild, tree.node_at(2));
    EXPECT_EQ(tree.to_level_strings(),
              (std::vector<std::string>{"8", "4", "5"}));
}

TEST(CompetitiveProblem, PerformanceRegistryRunsCapturedCases) {
    bench::competitive::clear_performance_cases();

    bench::competitive::register_performance_case("quiet", quiet_answer, "11",
                                                  3);

    EXPECT_EQ(bench::competitive::performance_case_count(), std::size_t{1});

    std::ostringstream report;
    const auto summary = bench::competitive::run_performance_cases(report);

    EXPECT_EQ(summary.cases_run, std::size_t{1});
    EXPECT_EQ(summary.total_iterations, std::size_t{3});
    EXPECT_NE(report.str().find("quiet"), std::string::npos);
    EXPECT_NE(report.str().find("iterations=3"), std::string::npos);

    bench::competitive::clear_performance_cases();
}
