#Contributing to Newsflash

##How We Work
The Newsflash repository merges code from Pull Requests made from forked repositories. The Newsflash repository is updated from Pull Requests only. Code is never pushed directly to the repository.

###What's a Fork?
Start with this article on forking: [Fork a Repo](https://help.github.com/articles/fork-a-repo/)

*TL; DR:* Forking is a method developed by GitHub to copy a repository into your own account, or a team you manage. Then you can make changes to that repository to your heart's delight without affecting the code of the original repository.

###What's a Pull Request
Start with this article on pull requests: [Using pull requests](https://help.github.com/articles/using-pull-requests/)

Newsflash uses Pull Requests like any other open source project. If you have code that you would like added to the repository, create a Pull Request comparing the Master branch of of Newsflash to the branch of your Newsflash fork that you'd like merged. Pull Requests must be made from a branch in your fork, _not the Master branch_. So please work in a branch on your fork!

##How to Get Going
###Fork the Newsflash Repository
<img src="https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/fork.png" width=400>

Before you can start writing code to improve Newsflash, you need to fork the Newsflash repository. This will create a complete copy of Newsflash in your own GitHub account.

###Clone and Add Remotes
Your fork is what you'll clone down to your local machine to make changes to.

	git clone git@github.com:<YOUR USER NAME>/newsflash.git

Once you have your fork cloned, you need to add the original Newsflash repo as a remote, preferably called `upstream` so that you can pull changes that other people make.

	git remote add upstream git@github.com:brassil/newsflash.git
	git remote -v

You should see four lines as a result of the last command, a `(fetch)` and `(push)` for both  `origin` (your repository) and `upstream` (the original Newsflash repository).

###Make Changes
All your work should be done in a branch that is well named. By well named, we mean it describes what you're working on in that branch. You can create a new branch with the command 

	git checkout -b my_new_branch

The `-b` flag creates and then checksout the new branch.

While you work, commit often so that you can roll back work if you need to. Stay up to date with changes made to the original repository as you'll be required to merge in any new additions to the Newsflash repository before you can submit your code for inclusion. At any point, but _always_ before pushing your code to your remote repository, you should rebase with master.

Rebasing makes sure that the changes you made can be merged into the code base of the original repository without problems, and then applies the changes from one branch ontop of the changes made in another branch. There are just a few basic steps to rebasing to incorporate new changes into your branch.

1. Checkout the `master` branch of your repository
	git checkout master

2. Pull any new changes from the `upstream` repository (the global Newsflash repo in this case). Assuming you didn't make any changes in your local `master` branch - you shouldn't have any problems merging in the updates from `upstream`.
	git pull upstream master

3. Checkout your branch once again.
	git checkout my_new_branch

4. Rebase with `master`. If there are any conflicts - git will do its best to walk you through them and help you merge them.
	git rebase master

###Preparing your Changes
Once you've got your work squared away and you're confident that your changes are mergable, because you've pulled new changes from `upstream` and rebased with your `master` branch, it's time to squash commits. If you've been committing early and often, you will likely have many commits in your branch that make up all the changes you made. We want to squash all those commits into a single commit to make the Pull Request process cleaner. We accomplish this with an interactive rebase.

	git rebase -i master

This opens an interactive script in your terminal that lists all of the commits in the branch. Each one will be marked as `pick` meaning that at first, every single commit will be included independently. We want to combine all our commits into one.

<img src="https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/interactive_rebase.png" width=400>

You pick the commits that you want to keep by keeping the `pick` marker present. The rest of the commits can be squashed by changing the status to `squash`. Note that the commits are listed in reverse chronological order. In general, the safe bet is to pick the 'first' commit (the earliest one chronologically) and squash the later commits onto it.

<img src="https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/pick_and_squash.png" width=400>

Exit from this first screen by saving and exiting (`:x` does the trick). You'll next need to create the commit message for the combined commit you're creating. Remove your previous commit messages if they're no longer helpful and make sure that the commit message you do provide is helpful in understanding what the full scope of the combined commit is.

<img src="https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/squashed_message.png" width=400>

If everything went according to plan, you'll be presented with a happy success screen:

<img src="https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/success_message.png" width=400>

###Submitting your Changes
Once you've successfully rebased and squashed, it's finally time to push and submit your code for review! Push your code to your remote branch
	git push origin my_new_branch

Now your new code is merge-ready and online, prepped for a Pull Request. Pull Requests are a formal process created by GitHub to submit your code for review by the managers of a repository, and provide them the means to merge it into the public repository should they feel the need. Create a Pull Request by visiting the original [Newsflash repository](https://github.com/brassil/newsflash). You should see a bright green button to create a new Pull Request:

<img src="https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/create_pull_request.png" width=400>

Click this button to get the form to describe your pull request:

<img src="https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/open_pull_request.png" width=400>

Compare the `master` branch of the `brassil/newsflash` repository with the branch you've been working in, in your fork. You might need to select the "compare across forks" to see the list of available forks to choose from. Once you've determined what branch you'll be submitting a PR for, check that the "automatic merge" check runs successfully (note the green "Able to Merge" checkbox). If an automatic merge is not possible, it means you didn't pull and rebase properly. If an automatic merge is possible, fill out the title and content boxes describing your pull request. Follow the tips of [this article on writing pull requests](https://github.com/blog/1943-how-to-write-the-perfect-pull-request).

<img src="https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/pull_request_body.png" width=400>

Once you've filled out the form, select "Create pull request" to create one. One of the adminstrators of the Newsflash repository will review your code by pulling and running it. Your pull request should include any information needed to run and test your code. GitHub has great discussion tools for commenting directly on PRs. This is where repository administrators will provide feedback. If a chance is necessary, simply make your changes, rebase as before, and push to your branch once again. GitHub will automatically update the Pull Request with your new code. 

<img src="https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/pull_request_conversation.png" width=400>

In general, one Newsflash admin will review your work. Once your code has been proved functional and valuable, they'll merge it in with the `upstream master` branch - making your changes an official part of Newsflash. This merge automatically closes the Pull Request.

<img src="https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/merge.png" width=400>

###Celebrate!
Hooray! You successfully contributed to Newsflash! :beers:

[fork]: https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/fork.png
[interactive_rebase]: https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/interactive_rebase.png
[pick_and_squash]: https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/pick_and_squash.png
[squashed_message]: https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/squashed_message.png
[success_message]: https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/success_message.png
[create_pull_request]: https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/create_pull_request.png
[open_pull_request]: https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/open_pull_request.png
[pull_request_body]: https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/pull_request_body.png
[pull_request_conversation]: https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/pull_request_conversation.png
[merge]: https://raw.githubusercontent.com/ahadik/newsflash/guidelines/info_assets/merge.png