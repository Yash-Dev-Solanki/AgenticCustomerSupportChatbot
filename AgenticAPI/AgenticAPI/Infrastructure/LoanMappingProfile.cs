using AutoMapper;
using DomainModels = AgenticAPI.Domain;
using ApplicationModels = AgenticAPI.Application.GetLoanStatement;

public class LoanMappingProfile : Profile
{
    public LoanMappingProfile()
    {
        CreateMap<DomainModels.LoanDetails, ApplicationModels.GetLoanStatementResponseModel>()
            .ForMember(dest => dest.PaymentHistory, opt => opt.Ignore());

        CreateMap<DomainModels.LoanPayment, ApplicationModels.LoanPayment>();

        CreateMap<DomainModels.LoanDetails, ApplicationModels.LoanSummary>()
            .ForMember(dest => dest.LoanAmount, opt => opt.MapFrom(src => src.LoanAmount))
            .ForMember(dest => dest.InterestRate, opt => opt.MapFrom(src => src.InterestRate))
            .ForMember(dest => dest.TenureMonths, opt => opt.MapFrom(src => src.TenureMonths))
            .ForMember(dest => dest.EmiAmount, opt => opt.MapFrom(src => src.EmiAmount))
            .ForMember(dest => dest.StartDate, opt => opt.MapFrom(src => src.StartDate))
            .ForMember(dest => dest.Status, opt => opt.MapFrom(src => src.Status))
            .ForMember(dest => dest.NextEmiDueDate, opt => opt.MapFrom(src => src.NextEmiDueDate))
            .ForMember(dest => dest.OutstandingBalance, opt => opt.MapFrom(src => src.OutstandingBalance));
    }
}
