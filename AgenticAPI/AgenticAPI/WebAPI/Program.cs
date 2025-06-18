using MediatR;
using AutoMapper;
using AgenticAPI.Infrastructure;

var builder = WebApplication.CreateBuilder(args);

//Load configuration from appsettings
builder.Configuration
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
    .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: false, reloadOnChange: true)
    .AddEnvironmentVariables();

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddMediatR(cfg =>
{
    cfg.RegisterServicesFromAssembly(typeof(Program).Assembly);
});
builder.Services.AddAutoMapper(typeof(MapperProfile));
builder.Services.AddAutoMapper(typeof(LoanMappingProfile));
builder.Services.AddSingleton<IMongoService, MongoService>();
builder.Services.AddSingleton<IChatService, ChatService>();
builder.Services.AddSingleton<ILoanService, LoanService>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
