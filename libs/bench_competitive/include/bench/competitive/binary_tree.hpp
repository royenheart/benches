#pragma once

#include <cstddef>
#include <initializer_list>
#include <memory>
#include <optional>
#include <queue>
#include <sstream>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

namespace bench::competitive {

template <typename Node> struct binary_tree_node_traits {
    static auto& value(Node& node) { return node.val; }
    static Node*& left(Node& node) { return node.left; }
    static Node*& right(Node& node) { return node.right; }
};

template <typename Node, typename Traits = binary_tree_node_traits<Node>>
std::vector<std::string>
binary_tree_to_level_strings(Node* root, std::size_t max_nodes = 10000);

template <typename Node, typename Traits = binary_tree_node_traits<Node>>
std::string binary_tree_pretty(Node* root, std::size_t max_nodes = 10000);

namespace binary_tree_detail {

template <typename T> std::string value_to_string(const T& value) {
    std::ostringstream output;
    output << value;
    return output.str();
}

template <typename Node, typename Traits, typename Value>
std::unique_ptr<Node> make_node(const Value& value) {
    if constexpr (std::is_constructible<Node, const Value&>::value) {
        return std::make_unique<Node>(value);
    } else {
        auto node = std::make_unique<Node>();
        Traits::value(*node) = value;
        return node;
    }
}

inline void trim_trailing_nulls(std::vector<std::string>& values) {
    while (!values.empty() && values.back() == "null") {
        values.pop_back();
    }
}

template <typename Node, typename Traits>
void append_pretty(Node* node, const std::string& prefix,
                   const std::string& edge, bool is_last,
                   std::size_t& remaining_nodes, std::ostringstream& output) {
    if (node == nullptr || remaining_nodes == 0) {
        return;
    }

    --remaining_nodes;
    output << '\n'
           << prefix << edge << ": " << value_to_string(Traits::value(*node));

    Node* left = Traits::left(*node);
    Node* right = Traits::right(*node);
    const std::string child_prefix = prefix + (is_last ? "    " : "|   ");

    if (left != nullptr) {
        append_pretty<Node, Traits>(left, child_prefix,
                                    right == nullptr ? "`-- L" : "|-- L",
                                    right == nullptr, remaining_nodes, output);
    }
    if (right != nullptr) {
        append_pretty<Node, Traits>(right, child_prefix, "`-- R", true,
                                    remaining_nodes, output);
    }
}

} // namespace binary_tree_detail

template <typename Node, typename Traits = binary_tree_node_traits<Node>>
class BinaryTreeFixture {
  public:
    using node_type = Node;
    using traits_type = Traits;
    using value_type =
        std::decay_t<decltype(Traits::value(std::declval<Node&>()))>;
    using optional_value_type = std::optional<value_type>;

    BinaryTreeFixture() = default;

    explicit BinaryTreeFixture(std::initializer_list<value_type> values) {
        assign_dense(values.begin(), values.end());
    }

    explicit BinaryTreeFixture(
        std::initializer_list<optional_value_type> values) {
        assign_optional(values.begin(), values.end());
    }

    explicit BinaryTreeFixture(const std::vector<value_type>& values) {
        assign_dense(values.begin(), values.end());
    }

    explicit BinaryTreeFixture(const std::vector<optional_value_type>& values) {
        assign_optional(values.begin(), values.end());
    }

    BinaryTreeFixture(const BinaryTreeFixture&) = delete;
    BinaryTreeFixture& operator=(const BinaryTreeFixture&) = delete;
    BinaryTreeFixture(BinaryTreeFixture&&) noexcept = default;
    BinaryTreeFixture& operator=(BinaryTreeFixture&&) noexcept = default;

    Node* root() const { return root_; }

    bool empty() const { return nodes_.empty(); }

    std::size_t size() const { return nodes_.size(); }

    std::size_t level_size() const { return level_nodes_.size(); }

    Node* node_at(std::size_t level_index) const {
        return level_nodes_.at(level_index);
    }

    std::vector<std::string> to_level_strings() const {
        return binary_tree_to_level_strings<Node, Traits>(root_, nodes_.size());
    }

    std::string pretty() const {
        return binary_tree_pretty<Node, Traits>(root_, nodes_.size());
    }

  private:
    template <typename Iterator>
    void assign_dense(Iterator first, Iterator last) {
        std::vector<optional_value_type> values;
        for (auto it = first; it != last; ++it) {
            values.emplace_back(*it);
        }
        assign_optional(values.begin(), values.end());
    }

    template <typename Iterator>
    void assign_optional(Iterator first, Iterator last) {
        std::vector<optional_value_type> values(first, last);
        level_nodes_.assign(values.size(), nullptr);
        if (values.empty() || !values.front().has_value()) {
            return;
        }

        root_ = create_node(*values.front());
        level_nodes_[0] = root_;

        std::queue<Node*> parents;
        parents.push(root_);
        std::size_t value_index = 1;

        while (!parents.empty() && value_index < values.size()) {
            Node* parent = parents.front();
            parents.pop();

            if (value_index < values.size()) {
                Node* left_child = create_optional_node(values[value_index]);
                Traits::left(*parent) = left_child;
                level_nodes_[value_index] = left_child;
                if (left_child != nullptr) {
                    parents.push(left_child);
                }
                ++value_index;
            }

            if (value_index < values.size()) {
                Node* right_child = create_optional_node(values[value_index]);
                Traits::right(*parent) = right_child;
                level_nodes_[value_index] = right_child;
                if (right_child != nullptr) {
                    parents.push(right_child);
                }
                ++value_index;
            }
        }
    }

    Node* create_optional_node(const optional_value_type& value) {
        if (!value.has_value()) {
            return nullptr;
        }
        return create_node(*value);
    }

    Node* create_node(const value_type& value) {
        auto node = binary_tree_detail::make_node<Node, Traits>(value);
        Node* current = node.get();
        Traits::left(*current) = nullptr;
        Traits::right(*current) = nullptr;
        nodes_.push_back(std::move(node));
        return current;
    }

    std::vector<std::unique_ptr<Node>> nodes_;
    std::vector<Node*> level_nodes_;
    Node* root_ = nullptr;
};

template <typename Node, typename Traits = binary_tree_node_traits<Node>>
BinaryTreeFixture<Node, Traits> make_binary_tree(
    std::initializer_list<typename BinaryTreeFixture<Node, Traits>::value_type>
        values) {
    return BinaryTreeFixture<Node, Traits>(values);
}

template <typename Node, typename Traits = binary_tree_node_traits<Node>>
BinaryTreeFixture<Node, Traits>
make_binary_tree(std::initializer_list<
                 typename BinaryTreeFixture<Node, Traits>::optional_value_type>
                     values) {
    return BinaryTreeFixture<Node, Traits>(values);
}

template <typename Node, typename Traits = binary_tree_node_traits<Node>>
BinaryTreeFixture<Node, Traits> make_binary_tree(
    const std::vector<typename BinaryTreeFixture<Node, Traits>::value_type>&
        values) {
    return BinaryTreeFixture<Node, Traits>(values);
}

template <typename Node, typename Traits = binary_tree_node_traits<Node>>
BinaryTreeFixture<Node, Traits>
make_binary_tree(const std::vector<typename BinaryTreeFixture<
                     Node, Traits>::optional_value_type>& values) {
    return BinaryTreeFixture<Node, Traits>(values);
}

template <typename Node, typename Traits>
std::vector<std::string> binary_tree_to_level_strings(Node* root,
                                                      std::size_t max_nodes) {
    std::vector<std::string> values;
    if (root == nullptr || max_nodes == 0) {
        return values;
    }

    std::queue<Node*> nodes;
    nodes.push(root);
    std::size_t visited_nodes = 0;

    while (!nodes.empty() && visited_nodes < max_nodes) {
        Node* current = nodes.front();
        nodes.pop();

        if (current == nullptr) {
            values.push_back("null");
            continue;
        }

        ++visited_nodes;
        values.push_back(
            binary_tree_detail::value_to_string(Traits::value(*current)));
        nodes.push(Traits::left(*current));
        nodes.push(Traits::right(*current));
    }

    binary_tree_detail::trim_trailing_nulls(values);
    return values;
}

template <typename Node, typename Traits>
std::string binary_tree_pretty(Node* root, std::size_t max_nodes) {
    if (root == nullptr || max_nodes == 0) {
        return "null";
    }

    std::ostringstream output;
    std::size_t remaining_nodes = max_nodes;
    --remaining_nodes;
    output << binary_tree_detail::value_to_string(Traits::value(*root));

    Node* left = Traits::left(*root);
    Node* right = Traits::right(*root);
    if (left != nullptr) {
        binary_tree_detail::append_pretty<Node, Traits>(
            left, "", right == nullptr ? "`-- L" : "|-- L", right == nullptr,
            remaining_nodes, output);
    }
    if (right != nullptr) {
        binary_tree_detail::append_pretty<Node, Traits>(
            right, "", "`-- R", true, remaining_nodes, output);
    }

    return output.str();
}

} // namespace bench::competitive
