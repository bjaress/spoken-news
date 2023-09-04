
$NEWS = {
    "frogs" => {
        headline: (
            "An <a href='/wiki/Frog_Incident'>incident</a> " +
            "involving <a href='/wiki/Frog'>frogs</a> " +
            "occurred. For a variety of reasons, it takes " +
            "Wikipedia many characters to form a headline " +
            "about it, but this will be truncated for " +
            "Spreaker."),

        episode_title: (
            "An incident involving frogs occurred. For a variety " +
            "of reasons, it takes Wikipedia many characters to " +
            "form a headline about it, but this ..."),

        episode_contents: (<<~HEREDOC.strip
          INTRO
          
          An incident involving frogs occurred. For a variety of reasons, it takes Wikipedia many characters to form a headline about it, but this will be truncated for Spreaker.
          
          A frog thing happened.
          
          Frogs are cool.
          
          OUTRO
          HEREDOC
        ),

        episode_id: 111111,

        articles: {
          "Frog" => {
            latest: { id: 1},
            source: (<<~HEREDOC.strip
              Frogs are [[cool]].
              <ref>''International Journal of Because I Said So''</ref>
              HEREDOC
              )
            },
          "Frog_Incident" => {
            latest: { id: 2},
            source: "A [[frog]] thing happened."
            },
        },
    },
    "toads" => {
        headline: (
            "An <a href='/wiki/Toad_Incident'>incident</a> " +
            "involving <a href='/wiki/Toad'>toads</a> " +
            "occurred. For a variety of reasons, it takes " +
            "Wikipedia many characters to form a headline " +
            "about it, but this will be truncated for " +
            "Spreaker."),

        episode_title: (
            "An incident involving toads occurred. For a variety " +
            "of reasons, it takes Wikipedia many characters to " +
            "form a headline about it, but this ..."),

        episode_contents: (<<~HEREDOC.strip
          INTRO
          
          An incident involving toads occurred. For a variety of reasons, it takes Wikipedia many characters to form a headline about it, but this will be truncated for Spreaker.
          
          A toad thing happened.
          
          Toads are cool.
          
          OUTRO
          HEREDOC
        ),

        episode_id: 222222,

        articles: {
          "Toad" => {
            latest: { id: 3},
            source: "Toads are [[cool]]."
            },
          "Toad_Incident" => {
            latest: { id: 4},
            source: "A [[toad]] thing happened."
            },
        },
    },
    "the nobel prize" => {
        headline: (
            "The Nobel Prize in <a href='/wiki/Cloudoligy'>cloud " +
            "watching</a> was awarded to Tammy Bigglesworth (pictured)."),

        episode_title: (
            "The Nobel Prize in cloud watching was awarded to " +
            "Tammy Bigglesworth."),

        episode_contents: (<<~HEREDOC.strip
          INTRO
          
          The Nobel Prize in cloud watching was awarded to Tammy Bigglesworth.
          
          Cloudoligy is a made-up word.
          
          OUTRO
          HEREDOC
            ),

        episode_id: 333333,

        articles: {
          "Cloudoligy" => {
            latest: { id: 5},
            source: <<~HEREDOC.strip
            Cloudoligy (unlike
            meteorology (/ˌmiːti.əˈɹɑləd͡ʒi/)) is a [[made-up]] word.
            HEREDOC
            },
        },
    },
    "sports" => {
        headline: (
         "Wikipedia editors are obsessed with " +
         "<a href='/wiki/Sports'>sports</a> " +
         "<a href='/wiki/Championship'>championships</a>."),

        episode_title: (
          "Wikipedia editors are obsessed with sports championships."
        ),

        episode_id: 444444,

        articles: {
          "Sports" => {
            latest: { id: 6},
            source: (
              "Blah blah blah blah." +
              "\n\n" +
              "Blahdy blahdy blahdy blahdy blahdy blahdy." +
              "Blahdy blahdy blahdy blahdy blahdy blahdy." +
              "Blahdy blahdy blahdy blahdy blahdy blahdy." +
              "Blahdy blahdy blahdy blahdy blahdy blahdy." +
              "Blahdy blahdy blahdy blahdy blahdy blahdy." +
              "Blahdy blahdy blahdy blahdy blahdy blahdy." +
              "Blahdy blahdy blahdy blahdy blahdy blahdy." +
              "Blahdy blahdy blahdy blahdy blahdy blahdy." +
              "Blahdy blahdy blahdy blahdy blahdy blahdy." +
              "Blahdy blahdy blahdy blahdy blahdy blahdy." +
              "Blahdy blahdy blahdy blahdy blahdy blahdy."
              )
            },
          "Championship" => {
            latest: { id: 7},
            source: (
              "Yada yada yada yada." +
              "\n\n" +
              "Dee-dah dee-dah dee-dah dee-dah dee-dah dee-dah." +
              "Dee-dah dee-dah dee-dah dee-dah dee-dah dee-dah." +
              "Dee-dah dee-dah dee-dah dee-dah dee-dah dee-dah." +
              "Dee-dah dee-dah dee-dah dee-dah dee-dah dee-dah." +
              "Dee-dah dee-dah dee-dah dee-dah dee-dah dee-dah." +
              "Dee-dah dee-dah dee-dah dee-dah dee-dah dee-dah." +
              "Dee-dah dee-dah dee-dah dee-dah dee-dah dee-dah." +
              "Dee-dah dee-dah dee-dah dee-dah dee-dah dee-dah." +
              "Dee-dah dee-dah dee-dah dee-dah dee-dah dee-dah." +
              "Dee-dah dee-dah dee-dah dee-dah dee-dah dee-dah." +
              "Dee-dah dee-dah dee-dah dee-dah dee-dah dee-dah."
              )
            },
        },

        episode_contents: (<<~HEREDOC.strip
          INTRO
          
          Wikipedia editors are obsessed with sports championships.
          
          Yada yada yada yada.
         
          Blah blah blah blah.
          
          OUTRO
          HEREDOC
        ),
    },

    # article where only a section is linked to
    "bananas" => {
        articles: {
          "Banana" => {
            latest: { id: 7},
            source: <<~HEREDOC.strip
            Don't include this sentence.
            ==Peel==
            Banana peels are slippery.
            HEREDOC
            },
        },
    },
    "banana peels" => {
        headline: (
         "Someone slipped on a " +
         "<a href='/wiki/Banana#Peel'>banana peel</a>."),

        episode_id: 555555,

        episode_title: (
          "Someone slipped on a banana peel."
        ),

        episode_contents: (<<~HEREDOC.strip
          INTRO
          
          Someone slipped on a banana peel.
          
          Banana peels are slippery.
          
          OUTRO
          HEREDOC
        ),
    },
}
