# ssbbot
A bot for the Super Smash Bros. Subreddit that defines terms or retrieves character data when requested.

Goal: To help new competitive smash players learn game lingo and give current players an easier way to talk about characters within threads

<a class="card-button" href="https://www.reddit.com/r/smashbros/comments/6v7fy3/introducing_the_new_and_improved_20xxbot_ssb_bot/">Link to Reddit post</a>


<h2>Issue and Updates tracker</h2>
<h3>Issues:</h3>
<ol>
  <li>Term definitions: The bot can't grab certain wiki definitions properly. This is likely due to either improper tag-search on the bot's end or inconsistent html tagging on the ssbwiki</li>
  <li>Character data: Some characters' frame data tables are different due to having special attributes.</li>
  <li>Data scraping: Some characters have spaces between names or inconsistent url-naming on kurogane hammer so scraping must be fixed for them.</li>
</ol>

<h3>Potential Updates</h3>
<ol>
  <li>
    Allow bot to reply to "What is" questions instead of just "ssb_bot define/character_name" direct requests. Potential issues include replying to too many comments, but can be easily avoided using the input-editor in main.py.
  </li>
</ol>
