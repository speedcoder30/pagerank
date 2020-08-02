import os
import random
import re
import sys
from collections import Counter

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    page_probability={}
    num_outlink_pages= len(corpus[page])

    """Set dampning factor probablity to all the pages"""
    if num_outlink_pages == 0:
        for outlinkpage in corpus:
            page_probability.update({outlinkpage:1/len(corpus)})
        return page_probability

    damping_factor_probability = (1 - damping_factor) / len(corpus)

    for corpus_page in corpus:
        if corpus_page in corpus[page]:
            probability=damping_factor_probability+ (damping_factor*(1/num_outlink_pages))
            page_probability.update({corpus_page:probability})
        else:
            page_probability.update({corpus_page:damping_factor_probability})


    return page_probability


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    pages_list=list(corpus.keys())
    page=random.choices(pages_list)
    sample_page_list=list()
    final_page_probability={}
    for loop in range(n):
        page_probability = transition_model(corpus, page[0], damping_factor)
        probability_values=list(page_probability.values())
        page=random.choices(pages_list,probability_values)
        sample_page_list.append(page[0])
    page_counter=Counter(sample_page_list)
    print("Sample_Size", len(sample_page_list))
    for page in corpus:
        if page in page_counter:
            sample_count=page_counter[page]
            final_page_probability.update({page:sample_count/n})
        else:
            final_page_probability.update({page:0})
    return final_page_probability


def iterate_pagerank(corpus, damping_factor):


    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    size=len(corpus)

    initial_pageRank= {}
    for page in corpus:
        initial_pageRank.update({page:1/size})
        if len(corpus[page])==0:
            corpus.update({page:set(corpus.keys())})

    inlinks_corpus={}
    for page in corpus:
        for pageset in corpus[page]:
            if pageset in inlinks_corpus:
                value=inlinks_corpus[pageset]
                value.add(page)
            else:
                inlinks_corpus.update({pageset:{page}})

    print(corpus)
    print(initial_pageRank)
    print(inlinks_corpus)
    return pageRank(corpus,initial_pageRank,inlinks_corpus,damping_factor)

def pageRank(corpus,iterative_pageRank,inlinks_corpus,dampning_factor):

    """Sum(PR(i)/NumLinks(i)"""
    new_iterative_pageRank={}
    random_probability=(1-dampning_factor)/len(corpus)
    for page in corpus:
        pageRankSum = 0.0
        if page in inlinks_corpus:
            inlink_pages=inlinks_corpus[page]
            for inlinkpage in inlink_pages:
                inlinkPageRank=iterative_pageRank[inlinkpage]
                numOfLinks=len(corpus[inlinkpage])
                if numOfLinks!=0:
                    pageRankSum+=(inlinkPageRank/numOfLinks)

        finalPageRank=random_probability+dampning_factor*pageRankSum
        new_iterative_pageRank.update({page:finalPageRank})
    iteration_flag=False
    for page in iterative_pageRank:
        rank=iterative_pageRank[page]
        new_rank=new_iterative_pageRank[page]
        if (rank-new_rank)>0.001:
            iteration_flag=True
            break
    if iteration_flag:
        new_iterative_pageRank=pageRank(corpus,new_iterative_pageRank,inlinks_corpus,dampning_factor)
    return new_iterative_pageRank


if __name__ == "__main__":
    main()
