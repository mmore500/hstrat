import networkx as nx

from hstrat._auxiliary_lib import random_tree


def test_random_tree():
    """Tests that a random tree is in fact a tree."""
    T = random_tree(10, seed=1234)
    assert nx.is_tree(T)


def test_random_directed_tree():
    """Generates a directed tree."""
    T = random_tree(10, seed=1234, create_using=nx.DiGraph())
    assert T.is_directed()


def test_random_tree_using_generator():
    """Tests that creating a random tree with a generator works"""
    G = nx.Graph()
    T = random_tree(10, seed=1234, create_using=G)
    assert nx.is_tree(T)


# NetworkX is distributed with the 3-clause BSD license.

# ::

#    Copyright (C) 2004-2024, NetworkX Developers
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.

#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are
#    met:

#      * Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.

#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.

#      * Neither the name of the NetworkX Developers nor the names of its
#        contributors may be used to endorse or promote products derived
#        from this software without specific prior written permission.

#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#    OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.