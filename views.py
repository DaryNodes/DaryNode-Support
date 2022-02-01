import disnake


class confirm_button(disnake.ui.View):
    """Ticket close confirmation button"""

    def __init__(self, db):
        super().__init__(timeout=30)
        self.db = db

    @disnake.ui.button(
        label="Confirm",
        style=disnake.ButtonStyle.danger,
        custom_id="confirm_close",
        emoji="⚠️"
    )
    async def close(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        ticket_collection = self.db['tickets']
        ticket_doc = await ticket_collection.find_one(
            {"channel_id": str(interaction.channel.id)})
        if ticket_doc is None:
            return await interaction.send(f"This channel is not a ticket channel.")
        if ticket_doc['status'] == 'closed':
            return await interaction.send(f"This channel is already closed.")
        ticket_collection.update_one({"channel_id": str(interaction.channel.id)}, {
                                     "$set": {"status": "closed"}})
        await interaction.send(f"This ticket has been closed by {interaction.author.mention}.")
        return await interaction.channel.delete(reason=f"Closed by {interaction.author.name}.")

    @disnake.ui.button(
        label="Cancel",
        style=disnake.ButtonStyle.gray,
        custom_id="cancel_close",
    )
    async def cancel_close(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        return await interaction.send("OK! Cancelled", ephemeral=True)


class close_button(disnake.ui.View):
    """Close button for ticket channel"""

    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(
        label="Close",
        style=disnake.ButtonStyle.danger,
        custom_id="close_ticket",
        emoji="🔒"
    )
    async def close(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        pass
