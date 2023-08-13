##
## This file contains dummy source code for the notebook to use.
## It is used to test the parser.
##


async def download_github_repo(
  repo_url,
  dst_dir,
  print_progress = True,
  throttle_limit = 0.5,
) -> Tuple[RepoStruct, float]:
  # Start timer
  start_time = time.time()
  
  # Check if repo exists
  repo_exists = await utilities.does_repo_exist(repo_url=repo_url)
  if not repo_exists:
    raise MissingRepoException(f"Repo does not exist: {repo_url}")

  # Download repo
  repo_struct = await utilities.download(url=repo_url, dst_dir=dst_dir, print_progress=print_progress, throttle_limit=throttle_limit)
  if repo_struct is None:
    raise DownloadException(f"Failed to download repo: {repo_url}")

  # End timer
  end_time = time.time()
  elapsed_time = end_time - start_time

  return (repo_struct, elapsed_time)
