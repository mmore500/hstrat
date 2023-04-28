#pragma once
#ifndef HSTRAT_AUXLIB_DEREFASVALUEITERATOR_HPP_INCLUDE
#define HSTRAT_AUXLIB_DEREFASVALUEITERATOR_HPP_INCLUDE

#include <iterator>
#include <utility>

namespace hstrat_auxlib {

template <typename Iterator>
struct DerefAsValueIterator : public Iterator {

  // Inherit constructors from the base iterator class
  using Iterator::Iterator;

  // Construct from base iterator class instance
  explicit DerefAsValueIterator(const Iterator& it) : Iterator(it) { }

  // Define the value type as the type pointed to by the iterator
  using value_type = typename std::iterator_traits<Iterator>::value_type;

  // Override operator* to return by value instead of by reference
  value_type operator*() const {
      return Iterator::operator*();
  }

};

// Helper function to create a ByValueIterator without specifying the template argument
template <typename Iterator>
DerefAsValueIterator<Iterator> make_deref_as_value_iterator(Iterator it) {
    return DerefAsValueIterator<Iterator>{std::move(it)};
}

} // namespace hstrat_auxlib


#endif // #ifndef HSTRAT_AUXLIB_DEREFASVALUEITERATOR_HPP_INCLUDE
