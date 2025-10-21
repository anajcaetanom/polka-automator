graph [
    directed 0

    # =================================
    #              NODES
    # =================================

    # hosts
    node [ id 1 label "h1" type "host" ]
    node [ id 2 label "h2" type "host" ]
    node [ id 3 label "h3" type "host" ]
    node [ id 4 label "h4" type "host" ]

    # edge nodes
    node [ id 11 label "e1" type "leaf" ]
    node [ id 12 label "e2" type "leaf" ]
    node [ id 13 label "e3" type "leaf" ]
    node [ id 14 label "e4" type "leaf" ]

    # core nodes
    node [ id 21 label "s1" type "core" ] # vix
    node [ id 22 label "s2" type "core" ] # sp
    node [ id 23 label "s3" type "core" ] # mg
    node [ id 24 label "s4" type "core" ] # rj

    # =================================
    #               LINKS
    # =================================

    # hosts -- edge
    edge [ source 1 target 11 ]
    edge [ source 2 target 12 ]
    edge [ source 3 target 13 ]
    edge [ source 4 target 14 ]

    # edge -- core
    edge [ source 11 target 21 ] 
    edge [ source 12 target 22 ] 
    edge [ source 13 target 23 ] 
    edge [ source 14 target 24 ] 

    # intracore
    edge [ source 21 target 23 ] 
    edge [ source 21 target 24 ] 
    edge [ source 22 target 23 ]
    edge [ source 22 target 24 ] 
    edge [ source 23 target 24 ] 

]
