const {
    Client,
    GatewayIntentBits,
    Partials,
    EmbedBuilder,
    ButtonBuilder,
    ButtonStyle,
    ActionRowBuilder,
    InteractionType,
    ApplicationCommandOptionType,
    ActivityType,
    MessageFlags
} = require('discord.js');
const { config } = require('dotenv');
const fs = require('fs');
const path = require('path');
const fetch = (url, init) => import('node-fetch').then(module => module.default(url, init));

config();

const token = process.env.DISCORD_TOKEN;
const apiURL = process.env.API_ENDPOINT;
const GUILD_ID = process.env.GUILD_ID;
const OWNER_NAME = process.env.OWNER_NAME;

const activeThreads = {};

// Initialize the Discord client
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildPresences
    ],
    partials: [Partials.Channel]
});

function saveChannelData(guildId, channelId) {
    const fileName = `${guildId}.json`;
    const data = { saved_channel_id: [channelId] };

    try {
        fs.writeFileSync(path.join(__dirname, fileName), JSON.stringify(data, null, 4));
        console.log(`Channel data saved to '${fileName}'`);
    } catch (error) {
        console.error(`Error saving channel data: ${error.message}`);
    }
}

function loadChannelData(guildId) {
    const fileName = `${guildId}.json`;

    try {
        const data = fs.readFileSync(path.join(__dirname, fileName));
        return JSON.parse(data).saved_channel_id[0];
    } catch (error) {
        console.error(`Error loading channel data: ${error.message}`);
        return null;
    }
}

async function sendAIResponse(data, message) {
    const thinkingMessage = await message.channel.send('> Thinking...');
    try {
        const response = await fetch(apiURL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const responseData = await response.json();
            await thinkingMessage.edit(responseData.message.content);
        } else {
            throw new Error(`HTTP error - status: ${response.status}`);
        }
    } catch (error) {
        await message.channel.send(`> ❌ An error occurred: ${error.message}`);
    }
}

client.once('ready', async () => {
    console.log(`Logged in as ${client.user.tag}.`);

    try {
        const guild = client.guilds.cache.get(GUILD_ID);
        if (guild) {
            await guild.commands.set([
                {
                    name: 'setup',
                    description: 'Setup the Bot'
                },
                {
                    name: 'help',
                    description: 'Get a help menu!'
                },
                {
                    name: 'ask',
                    description: 'Ask something to Phi!',
                    options: [
                        {
                            name: 'model',
                            type: ApplicationCommandOptionType.String,
                            description: 'Choose a model to use',
                            required: true,
                            choices: [
                                { name: 'phi4 (slower)', value: 'phi4-mini:latest' },
                                { name: 'gemma3 (faster)', value: 'gemma3:1b' },
                                { name: 'deepseek-r1 (faster)', value: 'deepseek-r1:1.5b' },
                                { name: 'qwen2 (medium)', value: 'qwen2:1.5b' },
                                { name: 'llama3.2 (slower)', value: 'llama3.2:3b' }
                            ]
                        },
                        {
                            name: 'message',
                            type: ApplicationCommandOptionType.String,
                            description: 'The message you want to send',
                            required: false
                        }
                    ]
                }
            ]);
            console.log('Commands synced to guild.');
        }
    } catch (error) {
        console.error(`Error syncing commands: ${error.message}`);
    }
});

client.on('interactionCreate', async (interaction) => {
    if (interaction.type !== InteractionType.ApplicationCommand) return;

    const { commandName } = interaction;

    switch (commandName) {
        case 'setup': {
            const embed = new EmbedBuilder()
                .setTitle(`🔥 Setup`)
                .setColor(0xa020f0)
                .setDescription('Setup the Bot in the current channel. If you do, it can __only__ be used in this channel.')
                .setAuthor({ name: 'Phi-Trash - Setup' })
                .setFooter({ text: '/help to see all commands!' });

            const button = new ButtonBuilder()
                .setStyle(ButtonStyle.Primary)
                .setLabel('Setup this channel')
                .setEmoji('⚙️')
                .setCustomId('setup_button');

            const row = new ActionRowBuilder().addComponents(button);

            await interaction.reply({ embeds: [embed], components: [row], flags: MessageFlags.Ephemeral });

            const filter = (i) => i.customId === 'setup_button' && i.user.id === interaction.user.id;
            const collector = interaction.channel.createMessageComponentCollector({ filter, time: 60000 });

            collector.on('collect', async (i) => {
                const channel = i.channel;
                const legit = channel.members.some((member) => member.user.username === OWNER_NAME || member.user.username === 'nino.css');

                if (legit) {
                    await i.deferReply();
                    saveChannelData(interaction.guild.id, channel.id);
                    await i.editReply(`Setup completed! You can now use the Bot in ${channel}! 🎉`);
                } else {
                    await i.reply({ content: "Owner is not in this channel, couldn't start the setup.", ephemeral: true });
                }
            });
            break;
        }
        case 'help': {
            const channelId = loadChannelData(GUILD_ID);

            if (interaction.channel.id === channelId) {
                const emojis = ['🔥', '✨'];
                const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];

                const embed = new EmbedBuilder()
                    .setTitle(`${randomEmoji} Help`)
                    .setDescription('List of commands you can use:')
                    .setColor(0xa020f0)
                    .addFields(
                        { name: '/ask', value: 'Ask something to Phi-Trash!', inline: false },
                        { name: '', value: 'You can choose a Model:\n -> **phi4** *(slower, by Microsoft)* \
                            \n -> **gemma3** *(faster, by Google)* \n -> **deepseek-r1** *(faster, by Deepseek)* \
                            \n -> **qwen2** *(medium, by Alibaba)* \n -> **llama3.2** *(slower, by Meta)*', inline: false },
                        { name: '/help', value: 'Get this help menu!', inline: false },
                        { name: 'Github', value: '[Github](https://github.com/nino749)', inline: false }
                    )
                    .setFooter({ text: 'go to my Github to see the code!' })
                    .setTimestamp();

                await interaction.reply({ embeds: [embed] });
            } else {
                await interaction.reply({ content: "You can't use the Bot in this channel. Please use the setup command to set up the Bot in this channel.", ephemeral: true });
            }
            break;
        }
        case 'ask': {
            const model = interaction.options.getString('model');
            const message = interaction.options.getString('message');
            const channelId = loadChannelData(GUILD_ID);
            let threadId = 0;

            
            if (interaction.channel.id === channelId) {
                await interaction.reply('> Sending ✨');
                
                const thread = await interaction.channel.threads.create({
                    name: `Chat by ${interaction.user.username}`,
                    autoArchiveDuration: 60,
                    reason: `Thread created by ${interaction.user.username} for ${model}`,
                });
                const embed = new EmbedBuilder()
                    .setTitle('✨ Thread created!')
                    .setDescription(`> A new thread has been created for you, <@${interaction.user.id}>! Have fun in <#${thread.id}>!`)
                    .setColor(0xa020f0)
                    .addFields(
                        { name: 'Model:', value: `**${model}**`, inline: true },
                        { name: "Thread ID:", value: `**${thread.id}**`, inline: true },
                        { name: "Channel ID:", value: `**${channelId}**`, inline: true },
                    )
                    .setFooter({ text: 'You can now ask your question!' })
                    .setTimestamp();
                await interaction.editReply({ embeds: [embed], content: '' });

                activeThreads[thread.id] = {
                    model,
                    user_id: interaction.user.id,
                    last_message: ''
                };

                if (message) {
                    const data = {
                        model,
                        messages: [{ role: 'user', content: message }],
                        stream: false,
                        options: { temperature: 0.9, mirostat: 2 }
                    };
                    sendAIResponse(data, thread.lastMessage);
                }
            } else {
                await interaction.reply({ content: "You can't use the Bot in this channel. Please use the setup command to set up the Bot in this channel.", ephemeral: true });
            }
            break;
        }
        default:
            console.error(`Unknown command: ${commandName}`);
    }
});

client.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    if (message.channel.isThread() && activeThreads[message.channel.id]) {
        const threadInfo = activeThreads[message.channel.id];
        const model = threadInfo.model;

        const data = {
            model,
            messages: [{ role: 'user', content: message.content }],
            stream: false,
            options: { temperature: 0.9, mirostat: 2 }
        };

        sendAIResponse(data, message);
    }
});

client.login(token);