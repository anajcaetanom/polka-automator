graph [
    directed 0

    # =================================
    #              NODES
    # =================================

    # hosts H1 to H11
    node [ id 1 label "H1" type "host" ]
    node [ id 2 label "H2" type "host" ]
    node [ id 3 label "H3" type "host" ]
    node [ id 4 label "H4" type "host" ]
    node [ id 5 label "H5" type "host" ]
    node [ id 6 label "H6" type "host" ]
    node [ id 7 label "H7" type "host" ]
    node [ id 8 label "H8" type "host" ]
    node [ id 9 label "H9" type "host" ]
    node [ id 10 label "H10" type "host" ]
    node [ id 11 label "H11" type "host" ]

    # edge nodes (leafs) E1 to E10
    node [ id 12 label "E1" type "leaf" ]
    node [ id 13 label "E2" type "leaf" ]
    node [ id 14 label "E3" type "leaf" ]
    node [ id 15 label "E4" type "leaf" ]
    node [ id 16 label "E5" type "leaf" ]
    node [ id 17 label "E6" type "leaf" ]
    node [ id 18 label "E7" type "leaf" ]
    node [ id 19 label "E8" type "leaf" ]
    node [ id 20 label "E9" type "leaf" ]
    node [ id 21 label "E10" type "leaf" ]

    # core nodes S1 to S10
    node [ id 22 label "S1" type "core" ]
    node [ id 23 label "S2" type "core" ]
    node [ id 24 label "S3" type "core" ]
    node [ id 25 label "S4" type "core" ]
    node [ id 26 label "S5" type "core" ]
    node [ id 27 label "S6" type "core" ]
    node [ id 28 label "S7" type "core" ]
    node [ id 29 label "S8" type "core" ]
    node [ id 30 label "S9" type "core" ]
    node [ id 31 label "S10" type "core" ]

    # =================================
    #               LINKS
    # =================================

    edge [ source 1 target 12 ]
    edge [ source 11 target 12 ]
    edge [ source 12 target 22 ]

    edge [ source 2 target 13 ]
    edge [ source 13 target 23 ]

    edge [ source 3 target 14 ]
    edge [ source 14 target 24 ]

    edge [ source 4 target 15 ]
    edge [ source 15 target 25 ]

    edge [ source 5 target 16 ]
    edge [ source 16 target 26 ]

    edge [ source 6 target 17 ]
    edge [ source 17 target 27 ]

    edge [ source 7 target 18 ]
    edge [ source 18 target 28 ]

    edge [ source 8 target 19 ]
    edge [ source 19 target 29 ]

    edge [ source 9 target 20 ]
    edge [ source 20 target 30 ]

    edge [ source 10 target 21 ]
    edge [ source 21 target 31 ]

    edge [ 
        source 22 
        target 23 
        src_port "s1-eth2"
        dst_port "s2-eth2"
    ]

    edge [ 
        source 23 
        target 24 
        src_port "s2-eth3"
        dst_port "s3-eth2"
    ]

    edge [ 
        source 24 
        target 25 
        src_port "s24-eth3"
        dst_port "s25-eth2"
    ]

    edge [ 
        source 25 
        target 26 
        src_port "s25-eth3"
        dst_port "s26-eth2"
    ]

    edge [ 
        source 26 
        target 27 
        src_port "s26-eth3"
        dst_port "s27-eth2"
    ]

    edge [ 
        source 27 
        target 28 
        src_port "s27-eth3"
        dst_port "s28-eth2"
    ]

    edge [ 
        source 28 
        target 29 
        src_port "s28-eth3"
        dst_port "s29-eth2"
    ]
    edge [ 
        source 29 
        target 30 
        src_port "s29-eth3"
        dst_port "s30-eth2"
    ]

    edge [ 
        source 30 
        target 31 
        src_port "s30-eth3"
        dst_port "s31-eth2"
    ]

]