#pragma once

#include <cstddef>
#include <initializer_list>
#include <memory>
#include <type_traits>
#include <utility>
#include <vector>

namespace bench::competitive {

template <typename Node> struct list_node_traits {
    static auto& value(Node& node) { return node.val; }
    static Node*& next(Node& node) { return node.next; }
};

template <typename Node>
struct doubly_list_node_traits : list_node_traits<Node> {
    static Node*& prev(Node& node) { return node.prev; }
};

namespace linked_list_detail {

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

} // namespace linked_list_detail

template <typename Node, typename Traits = list_node_traits<Node>>
std::vector<std::decay_t<decltype(Traits::value(std::declval<Node&>()))>>
linked_list_to_vector(Node* start, std::size_t max_nodes) {
    using value_type =
        std::decay_t<decltype(Traits::value(std::declval<Node&>()))>;

    std::vector<value_type> values;
    values.reserve(max_nodes);
    for (Node* current = start; current != nullptr && values.size() < max_nodes;
         current = Traits::next(*current)) {
        values.push_back(Traits::value(*current));
    }
    return values;
}

template <typename Node, typename Traits = list_node_traits<Node>>
class SinglyListFixture {
  public:
    using node_type = Node;
    using traits_type = Traits;
    using value_type =
        std::decay_t<decltype(Traits::value(std::declval<Node&>()))>;

    SinglyListFixture() = default;

    explicit SinglyListFixture(std::initializer_list<value_type> values) {
        assign(values.begin(), values.end());
    }

    explicit SinglyListFixture(const std::vector<value_type>& values) {
        assign(values.begin(), values.end());
    }

    SinglyListFixture(const SinglyListFixture&) = delete;
    SinglyListFixture& operator=(const SinglyListFixture&) = delete;
    SinglyListFixture(SinglyListFixture&&) noexcept = default;
    SinglyListFixture& operator=(SinglyListFixture&&) noexcept = default;

    Node* head() const { return head_; }

    bool empty() const { return nodes_.empty(); }

    std::size_t size() const { return nodes_.size(); }

    Node* node_at(std::size_t index) const { return nodes_.at(index).get(); }

    std::vector<value_type> to_vector() const { return to_vector(head_); }

    std::vector<value_type> to_vector(Node* start) const {
        return to_vector(start, nodes_.size());
    }

    std::vector<value_type> to_vector(Node* start,
                                      std::size_t max_nodes) const {
        return linked_list_to_vector<Node, Traits>(start, max_nodes);
    }

  private:
    template <typename Iterator> void assign(Iterator first, Iterator last) {
        Node* tail = nullptr;
        for (auto it = first; it != last; ++it) {
            auto node = linked_list_detail::make_node<Node, Traits>(*it);
            Node* current = node.get();
            Traits::next(*current) = nullptr;

            if (tail == nullptr) {
                head_ = current;
            } else {
                Traits::next(*tail) = current;
            }

            tail = current;
            nodes_.push_back(std::move(node));
        }
    }

    std::vector<std::unique_ptr<Node>> nodes_;
    Node* head_ = nullptr;
};

template <typename Node, typename Traits = doubly_list_node_traits<Node>>
class DoublyListFixture {
  public:
    using node_type = Node;
    using traits_type = Traits;
    using value_type =
        std::decay_t<decltype(Traits::value(std::declval<Node&>()))>;

    DoublyListFixture() = default;

    explicit DoublyListFixture(std::initializer_list<value_type> values) {
        assign(values.begin(), values.end());
    }

    explicit DoublyListFixture(const std::vector<value_type>& values) {
        assign(values.begin(), values.end());
    }

    DoublyListFixture(const DoublyListFixture&) = delete;
    DoublyListFixture& operator=(const DoublyListFixture&) = delete;
    DoublyListFixture(DoublyListFixture&&) noexcept = default;
    DoublyListFixture& operator=(DoublyListFixture&&) noexcept = default;

    Node* head() const { return head_; }

    bool empty() const { return nodes_.empty(); }

    std::size_t size() const { return nodes_.size(); }

    Node* node_at(std::size_t index) const { return nodes_.at(index).get(); }

    std::vector<value_type> to_vector() const { return to_vector(head_); }

    std::vector<value_type> to_vector(Node* start) const {
        return to_vector(start, nodes_.size());
    }

    std::vector<value_type> to_vector(Node* start,
                                      std::size_t max_nodes) const {
        return linked_list_to_vector<Node, Traits>(start, max_nodes);
    }

  private:
    template <typename Iterator> void assign(Iterator first, Iterator last) {
        Node* tail = nullptr;
        for (auto it = first; it != last; ++it) {
            auto node = linked_list_detail::make_node<Node, Traits>(*it);
            Node* current = node.get();
            Traits::next(*current) = nullptr;
            Traits::prev(*current) = tail;

            if (tail == nullptr) {
                head_ = current;
            } else {
                Traits::next(*tail) = current;
            }

            tail = current;
            nodes_.push_back(std::move(node));
        }
    }

    std::vector<std::unique_ptr<Node>> nodes_;
    Node* head_ = nullptr;
};

template <typename Node, typename Traits = list_node_traits<Node>>
SinglyListFixture<Node, Traits> make_singly_list(
    std::initializer_list<typename SinglyListFixture<Node, Traits>::value_type>
        values) {
    return SinglyListFixture<Node, Traits>(values);
}

template <typename Node, typename Traits = list_node_traits<Node>>
SinglyListFixture<Node, Traits> make_singly_list(
    const std::vector<typename SinglyListFixture<Node, Traits>::value_type>&
        values) {
    return SinglyListFixture<Node, Traits>(values);
}

template <typename Node, typename Traits = doubly_list_node_traits<Node>>
DoublyListFixture<Node, Traits> make_doubly_list(
    std::initializer_list<typename DoublyListFixture<Node, Traits>::value_type>
        values) {
    return DoublyListFixture<Node, Traits>(values);
}

template <typename Node, typename Traits = doubly_list_node_traits<Node>>
DoublyListFixture<Node, Traits> make_doubly_list(
    const std::vector<typename DoublyListFixture<Node, Traits>::value_type>&
        values) {
    return DoublyListFixture<Node, Traits>(values);
}

} // namespace bench::competitive
