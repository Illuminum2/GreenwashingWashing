def match_site(pattern_prog, site):
    for page in site.pages:
        for word in page.content.split():
            if pattern_prog.search(word):
                page.matches.append(word)
