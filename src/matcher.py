def match_sites(prog, sites):
    matches = {}

    for site in sites:
        for word in site.content.split():
            if prog.search(word):
                if not site.url in matches:
                    matches[site.url] = []
                matches[site.url].append(word)

    return matches
